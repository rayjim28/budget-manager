from datetime import date
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import PersonalBudget, ExpenseItem, Income


class BudgetManagerIntegrationTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user('alice', password='A-long-password-123!')
        self.bob = User.objects.create_user('bob', password='B-long-password-123!')
        self.alice_budget = PersonalBudget.objects.create(owner=self.alice, budget_name='Household')
        self.bob_budget = PersonalBudget.objects.create(owner=self.bob, budget_name='Private budget')
        self.alice_income = Income.objects.create(owner=self.alice, budget=self.alice_budget, name='Paycheck', amount=Decimal('2500.00'))
        self.bob_income = Income.objects.create(owner=self.bob, budget=self.bob_budget, name='Private income', amount=Decimal('7000.00'))
        self.alice_expense = ExpenseItem.objects.create(owner=self.alice, budget=self.alice_budget, item_name='Food', item_cost=Decimal('50.00'), item_category='🛒', purchase_date=date(2026, 10, 14))
        self.bob_expense = ExpenseItem.objects.create(owner=self.bob, budget=self.bob_budget, item_name='Private expense', item_cost=Decimal('75.00'), item_category='🏠', purchase_date=date(2026, 10, 16))

    def test_login_required(self):
        for page in ('dashboard', 'index', 'transactions', 'reports', 'export_csv'):
            response = self.client.get(reverse(page))
            self.assertEqual(response.status_code, 302)

    def test_owner_only_budget_and_record_details(self):
        self.client.force_login(self.alice)
        pages = [
            reverse('detail', args=[self.bob_budget.pk]),
            reverse('income_detail', args=[self.bob_budget.pk, self.bob_income.pk]),
            reverse('expense_detail', args=[self.bob_budget.pk, self.bob_expense.pk]),
            reverse('income_edit', args=[self.bob_budget.pk, self.bob_income.pk]),
            reverse('expense_edit', args=[self.bob_budget.pk, self.bob_expense.pk]),
        ]
        for url in pages:
            self.assertEqual(self.client.get(url).status_code, 404)

    def test_dashboard_and_reports_are_user_scoped(self):
        self.client.force_login(self.alice)
        for route in ('dashboard', 'index', 'transactions', 'reports'):
            response = self.client.get(reverse(route))
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, 'Private budget')
            self.assertNotContains(response, 'Private expense')
            self.assertNotContains(response, '7000.00')
        self.assertContains(self.client.get(reverse('dashboard')), 'Household')

    def test_csv_contains_only_own_records(self):
        self.client.force_login(self.alice)
        result = self.client.get(reverse('export_csv'))
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result['Content-Type'], 'text/csv')
        self.assertIn('Food', result.content.decode())
        self.assertNotIn('Private expense', result.content.decode())

    def test_deleting_requires_post_and_ownership(self):
        self.client.force_login(self.alice)
        own_url = reverse('delete', args=[self.alice_budget.pk])
        other_url = reverse('delete', args=[self.bob_budget.pk])
        self.assertEqual(self.client.get(own_url).status_code, 405)
        self.assertEqual(self.client.post(other_url).status_code, 404)
        self.assertTrue(PersonalBudget.objects.filter(pk=self.alice_budget.pk).exists())
        self.assertEqual(self.client.post(own_url).status_code, 302)
        self.assertFalse(PersonalBudget.objects.filter(pk=self.alice_budget.pk).exists())
        self.assertTrue(PersonalBudget.objects.filter(pk=self.bob_budget.pk).exists())

    def test_creating_expense_requires_budget_ownership(self):
        self.client.force_login(self.alice)
        data = {'item_name': 'Supplies', 'item_cost': '19.95', 'item_category': '🛒', 'purchase_date': '2026-10-12'}
        self.assertEqual(self.client.post(reverse('create_expense', args=[self.bob_budget.pk]), data).status_code, 404)
        self.assertEqual(self.client.post(reverse('create_expense', args=[self.alice_budget.pk]), data).status_code, 302)
        self.assertTrue(ExpenseItem.objects.filter(owner=self.alice, item_name='Supplies').exists())

    def test_signup_and_login_pages_render(self):
        self.assertEqual(self.client.get(reverse('signup')).status_code, 200)
        self.assertEqual(self.client.get(reverse('login')).status_code, 200)
