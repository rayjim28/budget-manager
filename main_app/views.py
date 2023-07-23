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


# Create your views here.
# View for home page
def home(request):
    print("Rendering home.html")
    return render(request, "home.html")


def about(request):
    print("Rendering about.html")
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
            print(f"User {user.username} successfully signed up and logged in")
            return redirect("index")
        else:
            error_message = "Invalid sign up - try again"

    # A bad POST or a GET request, so render signup template
    form = UserCreationForm()
    context = {"form": form, "error_message": error_message}
    return render(request, "registration/signup.html", context)


# View for the personal budget


@login_required
def index(request):
    user_budgets = PersonalBudget.objects.filter(owner=request.user)

    budget_data = [
        {"budget": budget, "remaining_total": budget.remaining_total}
        for budget in user_budgets
    ]

    if budget_data:
        return render(
            request,
            "budgets/index.html",
            {
                "budget_data": budget_data,
                "number_of_incomes": user_budgets.first().total_income_count,  # This may not be the best way if each budget has different income counts
            },
        )
    else:
        messages.info(request, "No budgets found. Create one!")
        return redirect("create")


# @login_required
# def index(request):
#     user_budgets = PersonalBudget.objects.filter(owner=request.user)

#     budget_data = []  # This will hold the combined data

#     if user_budgets.exists():
#         print(f"Found {user_budgets.count()} budgets for {request.user}")

#         for budget in user_budgets:

#             incomes = Income.objects.filter(budget=budget)

#             # Calculate total income for each budget
#             number_of_incomes = incomes.count()
#             total_income = (
#                 budget.related_incomes.aggregate(Sum("amount"))["amount__sum"] or 0
#             )
#             remaining_total = total_income - budget.total_expenses

#             budget_data.append({"budget": budget, "remaining_total": remaining_total})

#         return render(
#             request,
#             "budgets/index.html",
#             {
#                 "budget_data": budget_data,  # passing budget_data instead of user_budgets
#                 "number_of_incomes": number_of_incomes,
#             },
#         )
#     else:
#         print(f"No budgets found for {request.user}")
#         return redirect("create")


# budget
@classmethod
def create_budget(cls, owner, budget_name):
    return cls.objects.create(owner=owner, budget_name=budget_name)


@login_required
def create(request):
    if request.method == "POST":
        budget_name = request.POST.get("name")
        PersonalBudget.create_budget(request.user, budget_name)
        messages.success(request, "Your personal budget has been created!")
        return redirect("index")

    return render(request, "budgets/create.html")


# def create(request):
#     if request.method == "POST":
#         budget_name = request.POST.get("name")

#         # Create the budget
#         budget = PersonalBudget(owner=request.user, budget_name=budget_name)
#         budget.save()
#         print(f"Created budget with name '{budget_name}' for {request.user}")

#         messages.success(request, "Your personal budget has been created!")
#         return redirect("index")

#     return render(request, "budgets/create.html")


@login_required
def detail(request, budget_id):
    budget = get_object_or_404(PersonalBudget, owner=request.user, id=budget_id)

    context = {
        "title": "Budget Detail",
        "budget": budget,
        "total_income": budget.total_income_count,
        "total_remaining": budget.remaining_total,
        "expense_count": budget.total_expenses,  # Assuming total_expenses returns the count
    }

    return render(request, "budgets/detail.html", context)


# @login_required
# def detail(request, budget_id):
#     budget = get_object_or_404(PersonalBudget, owner=request.user, id=budget_id)
#     incomes = Income.objects.filter(budget=budget)

#     total_income = incomes.count()
#     total_remaining = incomes.aggregate(Sum("amount"))["amount__sum"] or 0

#     context = {
#         "title": "Budget Detail",
#         "budget": budget,
#         "total_income": total_income,
#         "total_remaining": total_remaining,
#         "expense_count": budget.total_expense_count,
#     }

#     print(f"Showing details for budget_id: {budget_id}")
#     return render(request, "budgets/detail.html", context)


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
        budget_amount = request.POST.get("amount")

        if budget_name and budget_amount:
            budget.budget_name = budget_name
            budget.budget_amount = budget_amount
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


# @login_required
# def edit(request, budget_id):
#     budget = get_object_or_404(PersonalBudget, id=budget_id)

#     # Ensure the user is authorized to edit this budget
#     if request.user != budget.owner:
#         messages.error(request, "You are not authorized to edit this budget.")
#         return redirect("index")  # Redirect to the budget list page

#     if request.method == "POST":
#         budget_name = request.POST.get("name")
#         budget_amount = request.POST.get("amount")

#         if budget_name and budget_amount:
#             budget.budget_name = budget_name
#             budget.budget_amount = budget_amount
#             budget.save()

#             messages.success(request, "Budget updated successfully!")
#             return redirect(
#                 "detail", budget_id=budget.id
#             )  # Redirect to the budget detail page
#         else:
#             messages.error(
#                 request,
#                 "Failed to update the budget. Please check the provided values.",
#             )

#     context = {"budget": budget}
#     return render(request, "budgets/edit.html", context)


# @login_required
# def delete(request, budget_id):
#     budget = get_object_or_404(PersonalBudget, id=budget_id)
#     if request.user == budget.owner:
#         print(f"User {request.user} is authorized to delete budget with id {budget_id}")
#         budget.delete()
#         messages.success(request, "Budget deleted successfully.")
#         return redirect("index")
#     else:
#         print(
#             f"User {request.user} is not authorized to delete budget with id {budget_id}"
#         )
#         messages.error(request, "You are not authorized to delete this budget.")
#         return redirect("index")


@login_required
def create_expense(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)

    if request.method == "POST":
        data = {
            "item_name": request.POST.get("item_name"),
            "item_cost": request.POST.get("item_cost"),
            # "item_cost": Decimal(request.POST.get("item_cost")),  # Convert string to Decimal
            "item_category": request.POST.get("item_category"),
            "purchase_date": request.POST.get("purchase_date"),
            "owner": request.user,
            "budget": budget,  # This line sets the ForeignKey relationship
        }

        expense = ExpenseItem.create_expense(data)

        return redirect("expense_list", budget_id=budget_id)

    return render(request, "budgets/expenses/create_expense.html", {"budget": budget})


# @login_required
# def create_expense(request, budget_id):
#     budget = get_object_or_404(PersonalBudget, id=budget_id)

#     if request.method == "POST":
#         item_name = request.POST.get("item_name")
#         item_cost = request.POST.get("item_cost")
#         item_category = request.POST.get("item_category")
#         purchase_date = request.POST.get("purchase_date")

#         print(f"Received new expense creation request for budget with id {budget_id}")

#         expense = ExpenseItem(
#             item_name=item_name,
#             item_cost=item_cost,
#             item_category=item_category,
#             purchase_date=purchase_date,
#             owner=request.user,
#         )
#         expense.save()

#         # No need to add the expense to the budget, it's already associated.
#         budget.related_expenses.add(expense)

#         print(f"Expense with name '{item_name}' added to budget with id {budget_id}")

#         return redirect("expense_list", budget_id=budget_id)

#     return render(request, "budgets/expenses/create_expense.html", {"budget": budget})


# View for the list of expense items
@login_required
def expense_list(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)

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
            "expenses": budget.get_expenses(),
            "number_of_incomes": budget.get_incomes().count(),
            "remaining_total": budget.get_remaining_total(),
        },
    )


# @login_required
# def expense_list(request, budget_id):
#     budget = get_object_or_404(PersonalBudget, id=budget_id)
#     expenses = budget.related_expenses.all()
#     incomes = Income.objects.filter(budget=budget)
#     print(f"Found {expenses.count()} expenses for {request.user}")

#     number_of_incomes = incomes.count()
#     total_income = incomes.aggregate(Sum("amount"))["amount__sum"] or 0
#     total_expenses = budget.total_expenses

#     remaining_total = total_income - total_expenses

#     if request.method == "POST":
#         expense_id = request.POST.get("expense_id")
#         expense = get_object_or_404(ExpenseItem, id=expense_id)
#         if expense.owner == request.user:
#             print(
#                 f"User {request.user} is authorized to delete expense with id {expense_id}"
#             )
#             expense.delete()
#             # Redirect to the expense list after deletion
#             return redirect("expense_list", budget_id=budget_id)
#         else:
#             print(
#                 f"User {request.user} is not authorized to delete expense with id {expense_id}"
#             )
#             return HttpResponseBadRequest(
#                 "You are not authorized to delete this expense."
#             )  # Return an error response if the user is not authorized
#     print(f"Total Income: {total_income}")
#     print(f"Total Expenses: {total_expenses}")
#     print(f"Remaining Total: {remaining_total}")

#     return render(
#         request,
#         "budgets/expenses/expense_list.html",
#         {
#             "budget": budget,
#             "expenses": expenses,
#             "number_of_incomes": number_of_incomes,
#             # "total_income": total_income,
#             "remaining_total": remaining_total,
#         },
#     )


@login_required
def expense_detail(request, budget_id, expense_id):
    expense = get_object_or_404(ExpenseItem, id=expense_id)
    budget = get_object_or_404(PersonalBudget, id=budget_id)
    print(
        f"Showing details for expense with id {expense_id} of budget with id {budget_id}"
    )
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


# @login_required
# def expense_edit(request, budget_id, expense_id):
#     expense = get_object_or_404(ExpenseItem, id=expense_id)
#     budget = get_object_or_404(PersonalBudget, id=budget_id)  # Fetch the budget object
#     error_messages = []

#     if request.method == "POST":
#         expense.item_name = request.POST.get("item_name")
#         expense.item_cost = request.POST.get("item_cost")
#         expense.item_category = request.POST.get("item_category")

#         # Get the date value from the form data with a default value of None
#         purchase_date_str = request.POST.get("purchase_date", None)

#         if purchase_date_str and purchase_date_str.strip():
#             try:
#                 # Parse the date string to a datetime object
#                 purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
#                 expense.purchase_date = purchase_date
#             except ValueError:
#                 # Add an error message if the date format is invalid
#                 error_messages.append(
#                     "The date format is invalid. Please enter a valid date in YYYY-MM-DD format."
#                 )
#         else:
#             # Add an error message if the date field is empty or not provided
#             error_messages.append("The date field cannot be empty.")

#         if error_messages:
#             # Loop through and add all error messages
#             for error in error_messages:
#                 messages.error(request, error)
#             return render(
#                 request,
#                 "budgets/expenses/expense_edit.html",
#                 {"expense": expense, "budget": budget},
#             )

#         expense.save()
#         print(f"Updated expense with id {expense_id} for budget with id {budget_id}")
#         return redirect("expense_list", budget_id=budget_id)

#     return render(
#         request,
#         "budgets/expenses/expense_edit.html",
#         {"expense": expense, "budget": budget},
#     )


def expense_delete(request, budget_id, expense_id):
    expense = get_object_or_404(ExpenseItem, id=expense_id)
    if request.user == expense.owner:
        print(f"Deleted expense with id {expense_id} for {request.user}")
        expense.delete()

        # Redirect back to the list of expenses after successful deletion
        return redirect("expense_list", budget_id=budget_id)
    else:
        # Return an error response if the user is not authorized
        print(
            f"User {request.user} is not authorized to delete expense with id {expense_id}"
        )
        return HttpResponseBadRequest("You are not authorized to delete this expense.")


def income_list(request, budget_id):
    budget = get_object_or_404(PersonalBudget, id=budget_id)
    incomes = Income.objects.filter(budget=budget)
    print(f"Found {incomes.count()} incomes for {request.user}")  # Print incomes

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

            print(
                f"Added income '{income_name}' with amount {income_amount} for budget with id {budget_id}"
            )
            messages.success(request, "Income added successfully!")
            return redirect("income_list", budget_id=budget_id)
        else:
            messages.error(
                request, "Failed to add the income. Please check the provided values."
            )

    return render(request, "budgets/incomes/create_income.html", {"budget": budget})
