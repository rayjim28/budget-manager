from django.contrib import admin
from .models import PersonalBudget, ExpenseItem, Income

# Register your models here.
admin.site.register(PersonalBudget)
admin.site.register(ExpenseItem)
admin.site.register(Income)