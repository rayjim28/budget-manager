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
    # path("budgets/<int:budget_id>/incomes/<int:income_id>/", views.income_detail, name="income_detail"),
    # path("budgets/<int:budget_id>/incomes/<int:income_id>/edit/", views.income_edit, name="income_edit"),
    # path("budgets/<int:budget_id>/incomes/<int:income_id>/delete/", views.income_delete, name="income_delete"),
]


# path("", views.home, name="home"),
# path("about/", views.about, name="about"),

# path("create_budget/", views.create_budget, name="create_budget"),
# path("personal_budget/", views.personal_budget, name="personal_budget"),
# path("budget_detail/<int:budget_id>/", views.budget_detail, name="budget_detail"),
# path("delete_budget/<int:budget_id>/", views.delete_budget, name="delete_budget"),
# path(
#     "create_expense/<int:budget_id>/", views.create_expense, name="create_expense"
# ),
# path("expense_list/<int:budget_id>/", views.expense_list, name="expense_list"),
# path(
#     "expense_detail/<int:expense_id>/", views.expense_detail, name="expense_detail"
# ),
# path("expense_edit/<int:expense_id>/", views.expense_edit, name="expense_edit"),
# path("income_list/", views.income_list, name="income_list"),
