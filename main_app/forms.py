from django import forms
from .models import ExpenseItem, Income, PersonalBudget

class BudgetForm(forms.ModelForm):
    class Meta:
        model = PersonalBudget
        fields = ['budget_name']
        widgets = {'budget_name': forms.TextInput(attrs={'placeholder': 'e.g. Household expenses'})}

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = ExpenseItem
        fields = ['item_name', 'item_cost', 'item_category', 'purchase_date']
        widgets = {
            'item_name': forms.TextInput(attrs={'placeholder': 'e.g. Groceries'}),
            'item_cost': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
            'purchase_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }
    def clean_item_cost(self):
        cost = self.cleaned_data['item_cost']
        if cost <= 0:
            raise forms.ValidationError('Enter an amount greater than zero.')
        return cost

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['name', 'amount']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. Paycheck'}),
            'amount': forms.NumberInput(attrs={'min': '0.01', 'step': '0.01'}),
        }
    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise forms.ValidationError('Enter an amount greater than zero.')
        return amount
