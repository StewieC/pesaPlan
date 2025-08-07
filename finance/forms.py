from django import forms
from django.core.exceptions import ValidationError
from .models import Budget, Allocation

PREDEFINED_CATEGORIES = [
    ('Food', 'Food'),
    ('Transport', 'Transport'),
    ('Rent', 'Rent'),
    ('Entertainment', 'Entertainment'),
    ('Other', 'Other (Specify)'),
]

class BudgetForm(forms.ModelForm):
    month = forms.CharField(
        max_length=7,
        help_text="Enter month in YYYY-MM format (e.g., 2025-08)",
        widget=forms.TextInput(attrs={'placeholder': 'YYYY-MM'})
    )

    class Meta:
        model = Budget
        fields = ['month', 'total_amount']
        widgets = {
            'total_amount': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
        }

    def clean_month(self):
        month = self.cleaned_data['month']
        if not month.match(r'^\d{4}-\d{2}$'):
            raise ValidationError("Month must be in YYYY-MM format")
        return month

    def clean_total_amount(self):
        total_amount = self.cleaned_data['total_amount']
        if total_amount <= 0:
            raise ValidationError("Total amount must be positive")
        return total_amount

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
            cleaned_data['custom_category'] = ''  # Ignore custom_category if not 'Other'

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