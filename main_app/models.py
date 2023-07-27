from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum


# Create your models here.
class PersonalBudget(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    budget_name = models.CharField(max_length=200)
    creation_date = models.DateField(auto_now_add=True)
    related_incomes = models.ManyToManyField("Income")
    
    @property
    def total_income(self):
        return self.income_set.aggregate(Sum("amount"))["amount__sum"] or 0
    
    @property
    def total_income_count(self):
        return self.related_incomes.count()
    
    @property
    def get_incomes(self):
        return self.related_incomes.all()

    @property
    def total_expenses(self):
        return self.expenses.aggregate(Sum("item_cost"))["item_cost__sum"] or 0

    @property
    def get_expenses_count(self):
        return self.expenses.count()
    
    @property
    def remaining_total(self):
        return self.total_income - self.total_expenses

   
    
    @classmethod
    def create_budget(cls, owner, budget_name):
        return cls.objects.create(owner=owner, budget_name=budget_name)

    

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

    @property
    def total(self):
        return self.expenses.aggregate(Sum("item_cost"))["item_cost__sum"] or 0

    @property
    def all(self):
        return self.expenses.all()
    

class Income(models.Model):
    amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    name = models.CharField(max_length=200, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    budget = models.ForeignKey(
        PersonalBudget, on_delete=models.CASCADE, null=True, blank=True
    )

    @property
    def total_income_count(self):
        # This will count all incomes related to the budget of this income instance.
        return Income.objects.filter(budget=self.budget).count()

    @property
    def total(self):
        # This will sum the amount of all incomes related to the budget of this income instance.
        return Income.objects.filter(budget=self.budget).aggregate(Sum("amount"))["amount__sum"] or 0
    
    @property
    def all(self):
        return self.incomes.all()


    # @property
    # def total_income_count(self):
    #     return self.related_incomes.count()

    # @property
    # def total(self):
    #     return self.related_incomes.aggregate(Sum("amount"))["amount__sum"] or 0
    
    