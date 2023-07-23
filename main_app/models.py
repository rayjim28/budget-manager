from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Create your models here.
class PersonalBudget(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    budget_name = models.CharField(max_length=200)
    creation_date = models.DateField(auto_now_add=True)
    # related_expenses = models.ManyToManyField("ExpenseItem")
    related_incomes = models.ManyToManyField("Income")
    
    @property
    def total_income(self):
        return self.related_incomes.aggregate(Sum("amount"))["amount__sum"] or 0

    @property
    def total_expenses(self):
        return self.expenses.aggregate(Sum("item_cost"))["item_cost__sum"] or 0

    
    @property
    def remaining_total(self):
        return self.total_income - self.total_expenses

    @property
    def total_income_count(self):
        return self.related_incomes.count()

    # @property
    # def total_expense_count(self):
    #     return self.related_expenses.count()

    # @property
    # def total_income_count(self):
    #     return self.related_incomes.count()

    # @property
    # def total_expenses(self):
    #     return self.related_expenses.aggregate(sum=models.Sum("item_cost"))["sum"] or 0
    
    # @property
    # def remaining_total(self):
    #     total_income = self.related_incomes.aggregate(Sum("amount"))["amount__sum"] or 0
    #     return total_income - self.total_expenses


    # # def get_total_remaining(self):
    # #     total_expenses = self.related_expenses.aggregate(sum=Sum("item_cost"))["sum"] or 0
    # #     total_income = self.related_incomes.aggregate(sum=Sum("amount"))["sum"] or 0
    # #     # total_expenses = total_expenses or 0
    # #     # total_income = total_income or 0
    # #     return self. + total_income - total_expenses


class ExpenseItem(models.Model):
    EXPENSE_CATEGORIES = [
        ("🏠", "Housing"),
        ("🏥", "Medical"),
        ("🛒", "Groceries"),
        ("🚙", "Car"),
    ]
    item_name = models.CharField(max_length=200)
    item_cost = models.DecimalField(max_digits=8, decimal_places=2)
    item_category = models.CharField(max_length=2, choices=EXPENSE_CATEGORIES)
    purchase_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(PersonalBudget, on_delete=models.CASCADE, related_name='expenses', null=True)

    
    def is_owned_by(self, user):
        return self.owner == user

    @classmethod
    def create_expense(cls, data):
        expense = cls.objects.create(**data)
        return expense


    def update_expense(self, data):
        for key, value in data.items():
            setattr(self, key, value)
        self.save()

    def remove_expense(self):
        self.delete()


class Income(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    name = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(
        PersonalBudget, on_delete=models.CASCADE, null=True, blank=True
    )
