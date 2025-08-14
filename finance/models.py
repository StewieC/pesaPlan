from django.db import models
from django.contrib.auth.models import User

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.CharField(max_length=7)  # YYYY-MM format
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.month} - {self.total_amount} KSH"

class Allocation(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='allocations')
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    custom_category = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"{self.category} - {self.amount} KSH"

class IncomeSource(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=50, help_text="e.g., Mom, Scholarship, Part-time job")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Amount in KSH")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.source} - {self.amount} KSH"