from django import forms
from django.core.exceptions import ValidationError
from .models import Budget, Allocation

PREDEFINED_CATEGORIES = [
    ('Food', 'Food'),
    ('Transport', 'Transport'),
    ('Rent', 'Rent'),
    ('Entertainment', 'Entertainment'),
    ('Other', 'Other (Custom)'),
]

MONTHS = [
    ('01', 'January'),
    ('02', 'February'),
    ('03', 'March'),
    ('04', 'April'),
    ('05', 'May'),
    ('06', 'June'),
    ('07', 'July'),
    ('08', 'August'),
    ('09', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December'),
]

YEARS = [(str(year), str(year)) for year in range(2020, 2031)]

class BudgetForm(forms.ModelForm):
    month_choice = forms.ChoiceField(choices=MONTHS, label="Month")
    year_choice = forms.ChoiceField(choices=YEARS, label="Year")
    total_amount = forms.DecimalField(min_value=0.01, decimal_places=2, label="Total Budget (KSH)")

    class Meta:
        model = Budget
        fields = ['month', 'total_amount']
        widgets = {
            'month': forms.HiddenInput(),  # Hidden field to store YYYY-MM
            'total_amount': forms.NumberInput(attrs={'min': 0.01, 'step': 0.01}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.month:
            year, month = self.instance.month.split('-')
            self.initial['year_choice'] = year
            self.initial['month_choice'] = month

    def clean(self):
        cleaned_data = super().clean()
        month_choice = cleaned_data.get('month_choice')
        year_choice = cleaned_data.get('year_choice')
        total_amount = cleaned_data.get('total_amount')

        if month_choice and year_choice:
            cleaned_data['month'] = f"{year_choice}-{month_choice}"
        else:
            raise ValidationError("Please select both a month and a year.")

        if total_amount is not None and total_amount <= 0:
            raise ValidationError("Total amount must be positive.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.month = self.cleaned_data['month']
        if commit:
            instance.save()
        return instance

class AllocationForm(forms.ModelForm):
    category = forms.ChoiceField(choices=PREDEFINED_CATEGORIES, required=True)
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
            raise ValidationError("Please specify a custom category when selecting 'Other'")
        if category != 'Other' and custom_category:
            cleaned_data['custom_category'] = ''

        if amount and amount <= 0:
            raise ValidationError("Amount must be positive")

        if self.budget and amount:
            total_allocated = sum(alloc.amount for alloc in self.budget.allocations.all())
            if total_allocated + amount > self.budget.total_amount:
                raise ValidationError(f"Total allocations ({total_allocated + amount} KSH) exceed budget ({self.budget.total_amount} KSH)")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.cleaned_data['category'] == 'Other':
            instance.category = self.cleaned_data['custom_category']
        if commit:
            instance.save()
        return instance