from django import forms
from .models import Budget, Allocation, IncomeSource

class IncomeForm(forms.ModelForm):
    class Meta:
        model = IncomeSource
        fields = ['source', 'amount']

class BudgetForm(forms.ModelForm):
    month_choice = forms.ChoiceField(choices=[(f"{i:02d}", month) for i, month in enumerate([
        'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'], 1)], label="Month")
    year_choice = forms.ChoiceField(choices=[(str(year), str(year)) for year in range(2020, 2031)], label="Year")
    total_amount = forms.DecimalField(min_value=0.01, decimal_places=2, label="Total Budget (KSH)")

    class Meta:
        model = Budget
        fields = ['total_amount']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'min': 0.01, 'step': 0.01}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['month'] = forms.CharField(widget=forms.HiddenInput(), required=False)
        if self.instance and self.instance.month:
            year, month = self.instance.month.split('-')
            self.initial['year_choice'] = year
            self.initial['month_choice'] = f"{int(month):02d}"

    def clean(self):
        cleaned_data = super().clean()
        month_choice = cleaned_data.get('month_choice')
        year_choice = cleaned_data.get('year_choice')
        total_amount = cleaned_data.get('total_amount')

        if not month_choice or not year_choice:
            raise forms.ValidationError("Please select both a month and a year.")
        
        cleaned_data['month'] = f"{year_choice}-{month_choice.zfill(2)}"

        if total_amount is not None and total_amount <= 0:
            raise forms.ValidationError("Total amount must be positive.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.month = self.cleaned_data['month']
        if commit:
            instance.save()
        return instance

class AllocationForm(forms.ModelForm):
    category = forms.ChoiceField(choices=[
        ('Food', 'Food'), ('Transport', 'Transport'), ('Rent', 'Rent'),
        ('Entertainment', 'Entertainment'), ('Other', 'Other (Custom)'),
    ], required=True)
    custom_category = forms.CharField(max_length=50, required=False, help_text="Enter custom category if 'Other' is selected")

    class Meta:
        model = Allocation
        fields = ['category', 'custom_category', 'amount']
        widgets = {
            'amount': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
        }

    def __init__(self, *args, budget=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.budget = budget

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get('category')
        custom_category = cleaned_data.get('custom_category')
        amount = cleaned_data.get('amount')

        if category == 'Other' and not custom_category:
            raise forms.ValidationError("Please specify a custom category when selecting 'Other'")
        if category != 'Other' and custom_category:
            cleaned_data['custom_category'] = ''

        if amount and amount <= 0:
            raise forms.ValidationError("Amount must be positive")

        if self.budget and amount:
            total_allocated = sum(alloc.amount for alloc in self.budget.allocations.all())
            if total_allocated + amount > self.budget.total_amount:
                raise forms.ValidationError(f"Total allocations ({total_allocated + amount} KSH) exceed budget ({self.budget.total_amount} KSH)")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data['category'] == 'Other':
            instance.category = self.cleaned_data['custom_category']
        if commit:
            instance.save()
        return instance