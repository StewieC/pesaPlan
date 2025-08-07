from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    month = models.CharField(max_length=7, help_text="Format: YYYY-MM, e.g., 2025-08")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Budget for {self.month}"

    class Meta:
        unique_together = ('user', 'month')  # Prevent duplicate budgets for same user/month

class Allocation(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='allocations')
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.category}: {self.amount} KSH"