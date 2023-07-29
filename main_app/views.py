from django.shortcuts import render, redirect
from .models import ExpenseItem, Income, PersonalBudget
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages  # for success and error messages
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.db.models import Sum
from django.urls import reverse


# Create your views here.
# View for home page
def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


def signup(request):
    error_message = ""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the user to the db
            user = form.save()
            # Automatically log in the new user
            login(request, user)
            return redirect("index")
        else:
            error_message = "Invalid sign up - try again"

    # A bad POST or a GET request, so render signup template
    form = UserCreationForm()
    context = {"form": form, "error_message": error_message}
    return render(request, "registration/signup.html", context)


##############################################################################################################


# View for the personal budget
@login_required
def index(request):
    user_budgets = PersonalBudget.objects.filter(owner=request.user)
    incomes = Income.objects.filter(budget__in=user_budgets)

    budget_data = [
        {
            "budget": budget,
            "remaining_total": budget.remaining_total,
            "total_income": Income.objects.filter(budget=budget).aggregate(
                Sum("amount")
            )["amount__sum"]
            or 0,
        }
        for budget in user_budgets
    ]

    if budget_data:
        return render(
            request,
            "budgets/index.html",
            {
                "budget_data": budget_data,
            },
        )
    else:
        messages.info(request, "No budgets found. Create one!")
        return redirect("create")


# budget
@login_required
def create(request):
    if request.method == "POST":
        budget_name = request.POST.get("name")
        PersonalBudget.create_budget(request.user, budget_name)
        messages.success(request, "Your personal budget has been created!")
        return redirect("index")

    return render(request, "budgets/create.html")


@login_required
def detail(request, budget_id):
    budget = get_object_or_404(PersonalBudget, owner=request.user, id=budget_id)
    incomes = Income.objects.filter(budget=budget_id)

    context = {
        "title": "Budget Detail",
        "budget": budget,
        "total_income": incomes.first().total_income_count if incomes.exists() else 0,
        "total_remaining": budget.remaining_total,
        "expense_count": budget.total_expenses,
        "total_income_amount": Income.objects.filter(budget=budget_id).aggregate(
            Sum("amount")
        )["amount__sum"]
        or 0,
    }

    return render(request, "budgets/detail.html", context)


def user_authorized_for_budget(request, budget):
    return request.user == budget.owner


@login_required
def edit(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)

    if not user_authorized_for_budget(request, budget):
        messages.error(request, "You are not authorized to edit this budget.")
        return redirect("index")

    if request.method == "POST":
        budget_name = request.POST.get("name")

        if budget_name:  # Only check if budget_name is available
            budget.budget_name = budget_name
            budget.save()

            messages.success(request, "Budget updated successfully!")
            return redirect("detail", budget_id=budget.id)
        else:
            messages.error(
                request,
                "Failed to update the budget. Please check the provided values.",
            )

    context = {"budget": budget}
    return render(request, "budgets/edit.html", context)


@login_required
def delete(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)

    if not user_authorized_for_budget(request, budget):
        messages.error(request, "You are not authorized to delete this budget.")
        return redirect("index")

    budget.delete()
    messages.success(request, "Budget deleted successfully.")
    return redirect("index")


##############################################################################################################


@login_required
def create_expense(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)

    if request.method == "POST":
        data = {
            "item_name": request.POST.get("item_name"),
            "item_cost": request.POST.get("item_cost"),
            "item_category": request.POST.get("item_category"),
            "purchase_date": request.POST.get("purchase_date"),
            "owner": request.user,
            "budget": budget,  # This line sets the ForeignKey relationship
        }

        expense = ExpenseItem.create_expense(data)

        return redirect("expense_list", budget_id=budget_id)

    return render(request, "budgets/expenses/create_expense.html", {"budget": budget})


# View for the list of expense items
@login_required
def expense_list(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)
    incomes = Income.objects.filter(budget=budget)

    if request.method == "POST":
        expense_id = request.POST.get("expense_id")
        expense = get_object_or_404(ExpenseItem, id=expense_id)
        if expense.is_owned_by(request.user):
            expense.remove_expense()
            return redirect("expense_list", budget_id=budget_id)
        else:
            return HttpResponseBadRequest(
                "You are not authorized to delete this expense."
            )

    return render(
        request,
        "budgets/expenses/expense_list.html",
        {
            "budget": budget,
            "expenses": budget.expenses.all(),
            "number_of_incomes": incomes.first().total_income_count
            if incomes.exists()
            else 0,
            "remaining_total": budget.remaining_total,
        },
    )


@login_required
def expense_detail(request, budget_id, expense_id):
    expense = get_object_or_404(ExpenseItem, id=expense_id)
    budget = get_object_or_404(PersonalBudget, id=budget_id)

    return render(
        request,
        "budgets/expenses/expense_detail.html",
        {"expense": expense, "budget": budget},
    )


@login_required
def expense_edit(request, budget_id, expense_id):
    expense = get_object_or_404(ExpenseItem, id=expense_id)
    budget = get_object_or_404(PersonalBudget, id=budget_id)

    if request.method == "POST":
        data = {
            "item_name": request.POST.get("item_name"),
            "item_cost": request.POST.get("item_cost"),
            "item_category": request.POST.get("item_category"),
            "purchase_date": request.POST.get("purchase_date"),
        }

        # Error handling for date parsing is preserved in views for user feedback
        purchase_date_str = data["purchase_date"]
        if purchase_date_str and purchase_date_str.strip():
            try:
                # Parse the date string to a datetime object
                purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
                data["purchase_date"] = purchase_date
            except ValueError:
                messages.error(
                    request,
                    "The date format is invalid. Please enter a valid date in YYYY-MM-DD format.",
                )
                return render(
                    request,
                    "budgets/expenses/expense_edit.html",
                    {"expense": expense, "budget": budget},
                )
        else:
            messages.error(request, "The date field cannot be empty.")
            return render(
                request,
                "budgets/expenses/expense_edit.html",
                {"expense": expense, "budget": budget},
            )

        expense.update_expense(data)

        return redirect("expense_list", budget_id=budget_id)

    return render(
        request,
        "budgets/expenses/expense_edit.html",
        {"expense": expense, "budget": budget},
    )


def expense_delete(request, budget_id, expense_id):
    expense = get_object_or_404(ExpenseItem, id=expense_id)
    if request.user == expense.owner:
        expense.delete()

        # Redirect back to the list of expenses after successful deletion
        return redirect("expense_list", budget_id=budget_id)
    else:
        # Return an error response if the user is not authorized
        print(
            f"User {request.user} is not authorized to delete expense with id {expense_id}"
        )
        return HttpResponseBadRequest("You are not authorized to delete this expense.")


##############################################################################################################


def income_list(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)
    incomes = Income.objects.filter(budget=budget)

    income_count = incomes.count()
    total_income = incomes.aggregate(Sum("amount"))["amount__sum"] or 0

    return render(
        request,
        "budgets/incomes/income_list.html",
        {
            "incomes": incomes,
            "budget": budget,
            "total_income": total_income,
            "income_count": income_count,
        },
    )


@login_required
def create_income(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)

    if request.method == "POST":
        income_name = request.POST.get("name")
        income_amount = request.POST.get("amount")

        if income_name and income_amount:
            income = Income(
                name=income_name,
                amount=income_amount,
                owner=request.user,
                budget=budget,
            )
            income.save()

            messages.success(request, "Income added successfully!")
            return redirect("income_list", budget_id=budget_id)
        else:
            messages.error(
                request, "Failed to add the income. Please check the provided values."
            )

    return render(request, "budgets/incomes/create_income.html", {"budget": budget})


def income_detail(request, budget_id, income_id):
    income = get_object_or_404(Income, id=income_id)
    budget = get_object_or_404(PersonalBudget, id=budget_id)

    return render(
        request,
        "budgets/incomes/income_detail.html",
        {"income": income, "budget": budget},
    )


def income_edit(request, budget_id, income_id):
    income = get_object_or_404(Income, id=income_id)

    if request.method == "POST":
        income.name = request.POST.get("name")
        income.amount = request.POST.get("amount")
        income.save()

        # Redirect to the income list view using reverse
        redirect_url = reverse("income_list", args=[budget_id])
        return redirect(redirect_url)

    # Handle GET request
    context = {
        "income": income,
        "budget_id": budget_id,
    }
    return render(request, "budgets/incomes/income_edit.html", context)


def income_delete(request, budget_id, income_id):
    income = get_object_or_404(Income, id=income_id)
    if request.method == "POST":
        income.amount = request.POST.get("amount")
        income.delete()
        return redirect("income_list", budget_id=budget_id)
    return render(
        request,
        "budgets/incomes/income_confirm_delete.html",
        {"income": income, "budget_id": budget_id},
    )
