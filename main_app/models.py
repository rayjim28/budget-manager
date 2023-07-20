from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ExpenseItem(models.Model):
    EXPENSE_CATEGORIES = [
        ('HO', 'Housing'),
        ('ME', 'Medical'),
        ('GR', 'Groceries'),
        ('CA', 'Car'),
    ]
    item_name = models.CharField(max_length=200)
    item_cost = models.DecimalField(max_digits=8, decimal_places=2)
    item_category = models.CharField(max_length=2, choices=EXPENSE_CATEGORIES)
    purchase_date = models.DateField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
class Income(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    name = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

class PersonalBudget(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    budget_name = models.CharField(max_length=200)
    budget_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)  # Add budget_amount field
    creation_date = models.DateField(auto_now_add=True)
    related_expenses = models.ManyToManyField(ExpenseItem)
    related_incomes = models.ManyToManyField(Income)
