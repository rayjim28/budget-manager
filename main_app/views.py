import csv
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BudgetForm, ExpenseForm, IncomeForm
from .models import PersonalBudget, ExpenseItem, Income

ZERO = Decimal('0.00')


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


def signup(request):
    form = UserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('dashboard')
    return render(request, 'registration/signup.html', {'form': form})


def owned_budget(request, budget_id):
    return get_object_or_404(PersonalBudget, pk=budget_id, owner=request.user)


def owned_expense(request, budget, expense_id):
    return get_object_or_404(ExpenseItem, pk=expense_id, owner=request.user, budget=budget)


def owned_income(request, budget, income_id):
    return get_object_or_404(Income, pk=income_id, owner=request.user, budget=budget)


def summary(user):
    budgets = PersonalBudget.objects.filter(owner=user).order_by('-creation_date', '-pk')
    income = Income.objects.filter(owner=user, budget__owner=user)
    expenses = ExpenseItem.objects.filter(owner=user, budget__owner=user)
    total_income = income.aggregate(s=Sum('amount'))['s'] or ZERO
    total_expenses = expenses.aggregate(s=Sum('item_cost'))['s'] or ZERO
    return budgets, income, expenses, total_income, total_expenses


def budget_rows(budgets):
    rows = []
    for budget in budgets:
        received = Income.objects.filter(owner=budget.owner, budget=budget).aggregate(s=Sum('amount'))['s'] or ZERO
        spent = ExpenseItem.objects.filter(owner=budget.owner, budget=budget).aggregate(s=Sum('item_cost'))['s'] or ZERO
        pct = min(100, round(float(spent / received * 100))) if received else 0
        rows.append({'budget': budget, 'income': received, 'spent': spent, 'balance': received-spent, 'pct': pct, 'over': spent > received and received > 0})
    return rows


def activity_items(incomes, expenses, limit=None):
    # Income has no date in the original model; keep it undated instead of inventing one.
    items = [{'name': e.item_name, 'amount': e.item_cost, 'date': e.purchase_date, 'kind': 'expense', 'budget': e.budget, 'pk': e.pk, 'category': e.get_item_category_display()} for e in expenses.select_related('budget')]
    items += [{'name': i.name or 'Income', 'amount': i.amount, 'date': None, 'kind': 'income', 'budget': i.budget, 'pk': i.pk, 'category': 'Income'} for i in incomes.select_related('budget')]
    items.sort(key=lambda x: (x['date'] is not None, x['date'] or date.min, x['pk']), reverse=True)
    return items[:limit] if limit else items


@login_required
def dashboard(request):
    budgets, incomes, expenses, income, spent = summary(request.user)
    rows = budget_rows(budgets)
    recent = activity_items(incomes, expenses, 6)
    categories = []
    category_names = dict(ExpenseItem.EXPENSE_CATEGORIES)
    for key, label in ExpenseItem.EXPENSE_CATEGORIES:
        amount = expenses.filter(item_category=key).aggregate(s=Sum('item_cost'))['s'] or ZERO
        if amount:
            categories.append({'name': label, 'amount': amount, 'pct': min(100, round(float(amount/spent*100))) if spent else 0})
    # Monthly trends include dated expenses. The original Income model has no date field.
    from django.utils import timezone
    today = timezone.localdate()
    trend = []
    for offset in range(5,-1,-1):
        index = today.year*12+today.month-1-offset
        year, month_index = divmod(index, 12)
        mo = month_index+1
        cost = expenses.filter(purchase_date__year=year,purchase_date__month=mo).aggregate(s=Sum('item_cost'))['s'] or ZERO
        trend.append({'label': date(year,mo,1).strftime('%b'), 'amount': cost})
    top = max([t['amount'] for t in trend] + [ZERO])
    for item in trend:
        item['height'] = max(2, round(float(item['amount'] / top * 100))) if top else 2
    return render(request, 'budgets/dashboard.html', {'section':'dashboard','total_income':income,'total_expenses':spent,'balance':income-spent,'budget_rows':rows[:5],'budget_count':budgets.count(),'recent':recent,'categories':categories,'trend':trend})


@login_required
def index(request):
    budgets, _, _, _, _ = summary(request.user)
    return render(request, 'budgets/index.html', {'section':'budgets','budget_data':budget_rows(budgets)})


@login_required
def create(request):
    form = BudgetForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        budget=form.save(commit=False)
        budget.owner=request.user
        budget.save()
        messages.success(request, 'Budget created.')
        return redirect('detail',budget_id=budget.pk)
    return render(request,'budgets/create.html',{'section':'budgets','form':form})


@login_required
def detail(request,budget_id):
    budget=owned_budget(request,budget_id)
    row=budget_rows([budget])[0]
    incomes=Income.objects.filter(budget=budget,owner=request.user).order_by('-pk')
    expenses=ExpenseItem.objects.filter(budget=budget,owner=request.user).order_by('-purchase_date','-pk')
    return render(request,'budgets/detail.html',{'section':'budgets','budget':budget,'row':row,'incomes':incomes[:6],'expenses':expenses[:6]})


@login_required
def edit(request,budget_id):
    budget=owned_budget(request,budget_id)
    form=BudgetForm(request.POST or None,instance=budget)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request, 'Budget updated.')
        return redirect('detail',budget_id=budget.pk)
    return render(request,'budgets/edit.html',{'section':'budgets','budget':budget,'form':form})


@login_required
@require_POST
def delete(request,budget_id):
    budget=owned_budget(request,budget_id)
    budget.delete()
    messages.success(request, 'Budget deleted.')
    return redirect('index')


@login_required
def create_expense(request,budget_id):
    budget=owned_budget(request,budget_id)
    form=ExpenseForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        expense=form.save(commit=False)
        expense.owner=request.user
        expense.budget=budget
        expense.save()
        messages.success(request, 'Expense added.')
        return redirect('expense_list',budget_id=budget.pk)
    return render(request,'budgets/expenses/create_expense.html',{'section':'transactions','budget':budget,'form':form})


@login_required
def expense_list(request,budget_id):
    budget=owned_budget(request,budget_id)
    expenses=ExpenseItem.objects.filter(budget=budget,owner=request.user).order_by('-purchase_date','-pk')
    return render(request,'budgets/expenses/expense_list.html',{'section':'transactions','budget':budget,'expenses':expenses,'total_spent':expenses.aggregate(s=Sum('item_cost'))['s'] or ZERO})


@login_required
def expense_detail(request,budget_id,expense_id):
    budget=owned_budget(request,budget_id)
    expense=owned_expense(request,budget,expense_id)
    return render(request,'budgets/expenses/expense_detail.html',{'section':'transactions','budget':budget,'expense':expense})


@login_required
def expense_edit(request,budget_id,expense_id):
    budget=owned_budget(request,budget_id)
    expense=owned_expense(request,budget,expense_id)
    form=ExpenseForm(request.POST or None,instance=expense)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'Expense updated.')
        return redirect('expense_list',budget_id=budget.pk)
    return render(request,'budgets/expenses/expense_edit.html',{'section':'transactions','budget':budget,'expense':expense,'form':form})


@login_required
@require_POST
def expense_delete(request,budget_id,expense_id):
    budget=owned_budget(request,budget_id)
    owned_expense(request,budget,expense_id).delete()
    messages.success(request, 'Expense deleted.')
    return redirect('expense_list',budget_id=budget.pk)


@login_required
def income_list(request,budget_id):
    budget=owned_budget(request,budget_id)
    incomes=Income.objects.filter(budget=budget,owner=request.user).order_by('-pk')
    return render(request,'budgets/incomes/income_list.html',{'section':'transactions','budget':budget,'incomes':incomes,'total_income':incomes.aggregate(s=Sum('amount'))['s'] or ZERO})


@login_required
def create_income(request,budget_id):
    budget=owned_budget(request,budget_id)
    form=IncomeForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        item=form.save(commit=False)
        item.owner=request.user
        item.budget=budget
        item.save()
        messages.success(request,'Income added.')
        return redirect('income_list',budget_id=budget.pk)
    return render(request,'budgets/incomes/create_income.html',{'section':'transactions','budget':budget,'form':form})


@login_required
def income_detail(request,budget_id,income_id):
    budget=owned_budget(request,budget_id)
    income=owned_income(request,budget,income_id)
    return render(request,'budgets/incomes/income_detail.html',{'section':'transactions','budget':budget,'income':income})


@login_required
def income_edit(request,budget_id,income_id):
    budget=owned_budget(request,budget_id)
    income=owned_income(request,budget,income_id)
    form=IncomeForm(request.POST or None,instance=income)
    if request.method=='POST' and form.is_valid():
        form.save()
        messages.success(request,'Income updated.')
        return redirect('income_list',budget_id=budget.pk)
    return render(request,'budgets/incomes/income_edit.html',{'section':'transactions','budget':budget,'income':income,'form':form})


@login_required
def income_delete(request,budget_id,income_id):
    budget=owned_budget(request,budget_id)
    income=owned_income(request,budget,income_id)
    if request.method=='POST':
        income.delete()
        messages.success(request,'Income deleted.')
        return redirect('income_list',budget_id=budget.pk)
    return render(request,'budgets/incomes/income_confirm_delete.html',{'section':'transactions','budget':budget,'income':income})


@login_required
def transactions(request):
    budgets,incomes,expenses,_,_=summary(request.user)
    rows=activity_items(incomes,expenses)
    search=request.GET.get('q','').strip().lower()
    kind=request.GET.get('type','all')
    if search:
        rows=[r for r in rows if search in (r['name']+' '+r['category']+' '+(r['budget'].budget_name if r['budget'] else '')).lower()]
    if kind in ('income','expense'):
        rows=[r for r in rows if r['kind']==kind]
    return render(request,'budgets/transactions.html',{'section':'transactions','activity':rows,'q':search,'type':kind,'budgets':budgets})


@login_required
def reports(request):
    _,incomes,expenses,total_income,total_expenses=summary(request.user)
    categories=[]
    for category,label in ExpenseItem.EXPENSE_CATEGORIES:
        amount=expenses.filter(item_category=category).aggregate(s=Sum('item_cost'))['s'] or ZERO
        categories.append({'name':label,'amount':amount,'pct':min(100,round(float(amount / total_expenses * 100))) if total_expenses else 0})
    return render(request,'budgets/reports.html',{'section':'reports','income':total_income,'spent':total_expenses,'balance':total_income-total_expenses,'categories':categories})


@login_required
def export_csv(request):
    _,incomes,expenses,_,_=summary(request.user)
    response=HttpResponse(content_type='text/csv')
    response['Content-Disposition']='attachment; filename="budget-manager-transactions.csv"'
    writer=csv.writer(response)
    writer.writerow(['Type','Description','Amount','Category','Date','Budget'])
    for item in activity_items(incomes,expenses):
        writer.writerow([item['kind'],item['name'],str(item['amount']),item['category'],item['date'].isoformat() if item['date'] else '',item['budget'].budget_name if item['budget'] else ''])
    return response
