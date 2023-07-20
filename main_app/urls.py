from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("signup/", views.signup, name="signup"),
    path("create_budget/", views.create_budget, name="create_budget"),
    path("personal_budget/", views.personal_budget, name="personal_budget"),
    path("budget_detail/<int:budget_id>/", views.budget_detail, name="budget_detail"),
    path("delete_budget/<int:budget_id>/", views.delete_budget, name="delete_budget"),
    path(
        "create_expense/<int:budget_id>/", views.create_expense, name="create_expense"
    ),
    path("expense_list/<int:budget_id>/", views.expense_list, name="expense_list"),
    path(
        "expense_detail/<int:expense_id>/", views.expense_detail, name="expense_detail"
    ),
    path("expense_edit/<int:expense_id>/", views.expense_edit, name="expense_edit"),
    path("income_list/", views.income_list, name="income_list"),
]
