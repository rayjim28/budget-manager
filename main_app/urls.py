from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("signup/", views.signup, name="signup"),
    
    path("budgets/", views.index, name="index"),
    path("budgets/create/", views.create, name="create"),
    path("budgets/<int:budget_id>/", views.detail, name="detail"),
    path("budgets/<int:budget_id>/edit/", views.edit, name="edit"),
    path("budgets/<int:budget_id>/delete/", views.delete, name="delete"),
    
    path("budgets/<int:budget_id>/expenses/", views.expense_list, name="expense_list"),
    path("budgets/<int:budget_id>/expenses/create_expense/", views.create_expense, name="create_expense"),
    path("budgets/<int:budget_id>/expenses/<int:expense_id>/", views.expense_detail, name="expense_detail"),
    path("budgets/<int:budget_id>/expenses/<int:expense_id>/expense_edit/", views.expense_edit, name="expense_edit"),
    path("budgets/<int:budget_id>/expenses/<int:expense_id>/expense_delete/", views.expense_delete, name="expense_delete"),
    
    path("budgets/<int:budget_id>/incomes/", views.income_list, name="income_list"),
    path("budgets/<int:budget_id>/incomes/create/", views.create_income, name="create_income"),
    path("budgets/<int:budget_id>/incomes/<int:income_id>/", views.income_detail, name="income_detail"),
    path("budgets/<int:budget_id>/incomes/<int:income_id>/edit/", views.income_edit, name="income_edit"),
    path("budgets/<int:budget_id>/incomes/<int:income_id>/delete/", views.income_delete, name="income_delete"),
]
