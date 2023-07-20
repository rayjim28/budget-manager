from django.shortcuts import render, redirect
from .models import ExpenseItem, Income, PersonalBudget
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages  # for success and error messages
from django.http import HttpResponseBadRequest


# Create your views here.
# View for home page
def home(request):
    return render(request, "budgets/home.html")


def about(request):
    return render(request, "budgets/about.html")


def signup(request):
    error_message = ""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the user to the db
            user = form.save()
            # Automatically log in the new user
            login(request, user)
            return redirect("personal_budget")
        else:
            error_message = "Invalid sign up - try again"

    # A bad POST or a GET request, so render signup template
    form = UserCreationForm()
    context = {"form": form, "error_message": error_message}
    return render(request, "registration/signup.html", context)


def income_list(request):
    incomes = Income.objects.filter(owner=request.user)
    print(f"Found {incomes.count()} incomes for {request.user}")  # Print incomes
    return render(request, "budgets/income_list.html", {"incomes": incomes})


def create_budget(request):
    if request.method == "POST":
        budget_name = request.POST.get("name")
        budget_amount = request.POST.get(
            "amount"
        )  # Update the variable name to 'budget_amount'

        budget = PersonalBudget(
            owner=request.user, budget_name=budget_name, budget_amount=budget_amount
        )
        budget.save()
        print(
            f"Created budget with name '{budget_name}' for {request.user}"
        )  # Print budget creation
        messages.success(request, "Your personal budget has been created!")
        return redirect("personal_budget")

    return render(request, "budgets/create_budget.html")


# View for the personal budget
def personal_budget(request):
    try:
        user_budgets = PersonalBudget.objects.filter(owner=request.user)
        print(
            f"Found {user_budgets.count()} budgets for {request.user}"
        )  # Print budgets
        return render(
            request, "budgets/personal_budget.html", {"user_budgets": user_budgets}
        )
    except PersonalBudget.DoesNotExist:
        print(f"No budgets found for {request.user}")  # Print when no budgets found
        return redirect("create_budget")


def budget_detail(request, budget_id):
    budgets = PersonalBudget.objects.all()
    print(f"Showing details for budget_id: {budget_id}")  # Print budget details
    context = {"title": "Budget Detail", "budgets": budgets}
    return render(request, "budgets/budget_detail.html", context)


def delete_budget(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)
    if request.user == budget.owner:
        print(
            f"Deleted budget with id {budget_id} for {request.user}"
        )  # Print when a budget is deleted
        budget.delete()
        return (
            HttpResponseBadRequest()
        )  # Return a response indicating successful deletion
    else:
        return HttpResponseBadRequest(
            "You are not authorized to delete this budget."
        )  # Return an error response if the user is not authorized


def create_expense(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)

    if request.method == "POST":
        item_name = request.POST.get("item_name")
        item_cost = request.POST.get("item_cost")
        item_category = request.POST.get("item_category")
        purchase_date = request.POST.get("purchase_date")

        expense = ExpenseItem(
            item_name=item_name,
            item_cost=item_cost,
            item_category=item_category,
            purchase_date=purchase_date,
            owner=request.user,
        )
        expense.save()

        budget.related_expenses.add(expense)

        return redirect("expense_list", budget_id=budget_id)

    return render(request, "budgets/create_expense.html", {"budget": budget})


# View for the list of expense items
def expense_list(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)
    expenses = budget.related_expenses.all()
    print(f"Found {expenses.count()} expenses for {request.user}")  # Print expenses

    if request.method == "POST":
        expense_id = request.POST.get("expense_id")
        expense = get_object_or_404(ExpenseItem, id=expense_id)
        if expense.owner == request.user:
            expense.delete()
            return (
                HttpResponseBadRequest()
            )  # Return a response indicating successful deletion
        else:
            return HttpResponseBadRequest(
                "You are not authorized to delete this expense."
            )  # Return an error response if the user is not authorized

    return render(
        request, "budgets/expense_list.html", {"budget": budget, "expenses": expenses}
    )


def expense_detail(request, expense_id):
    expense = get_object_or_404(ExpenseItem, id=expense_id)
    return render(request, 'budgets/expense_detail.html', {'expense': expense})


def expense_edit(request, expense_id):
    expense = get_object_or_404(ExpenseItem, id=expense_id)

    if request.method == "POST":
        expense.item_name = request.POST.get("item_name")
        expense.item_cost = request.POST.get("item_cost")
        expense.item_category = request.POST.get("item_category")
        expense.purchase_date = request.POST.get("purchase_date")
        expense.save()
        return redirect("expense_list")

    return render(request, "budgets/expense_edit.html", {"expense": expense})
