from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.views.generic import CreateView, DetailView
from django.contrib import messages
from .models import Budget, Allocation
from .forms import BudgetForm, AllocationForm
import logging

logger = logging.getLogger(__name__)

@login_required
def dashboard_view(request):
    budgets = Budget.objects.filter(user=request.user).order_by('-created_at')
    latest_budget = budgets.first() if budgets.exists() else None
    context = {'budgets': budgets}
    if latest_budget:
        total_allocated = sum(alloc.amount for alloc in latest_budget.allocations.all())
        savings = latest_budget.total_amount - total_allocated
        over_budget_amount = abs(savings) if savings < 0 else 0
        context.update({
            'latest_budget': latest_budget,
            'total_allocated': total_allocated,
            'savings': savings,
            'over_budget_amount': over_budget_amount,
        })
    return render(request, 'finance/dashboard.html', context)

class BudgetCreateView(CreateView):
    model = Budget
    form_class = BudgetForm
    template_name = 'finance/budget_create.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Budget created! Now add allocations.")
        logger.info(f"User {self.request.user.username} created budget for {form.instance.month}")
        return response

    def get_success_url(self):
        return reverse('finance:budget_detail', kwargs={'pk': self.object.pk})

class AllocationCreateView(CreateView):
    model = Allocation
    form_class = AllocationForm
    template_name = 'finance/allocation_create.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['budget'] = get_object_or_404(Budget, pk=self.kwargs['budget_id'], user=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['budget'] = get_object_or_404(Budget, pk=self.kwargs['budget_id'], user=self.request.user)
        return context

    def form_valid(self, form):
        form.instance.budget = get_object_or_404(Budget, pk=self.kwargs['budget_id'], user=self.request.user)
        response = super().form_valid(form)
        messages.success(self.request, f"Allocated {form.instance.amount} KSH to {form.instance.category}")
        logger.info(f"User {self.request.user.username} allocated {form.instance.amount} KSH to {form.instance.category}")
        return response

    def get_success_url(self):
        return reverse('finance:budget_detail', kwargs={'pk': self.kwargs['budget_id']})
class BudgetDetailView(DetailView):
    model = Budget
    template_name = 'finance/budget_detail.html'

    def get_object(self):
        return get_object_or_404(Budget, pk=self.kwargs['pk'], user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        allocations = self.object.allocations.all()
        total_allocated = sum(alloc.amount for alloc in allocations)
        savings = self.object.total_amount - total_allocated
        context['allocations'] = allocations
        context['total_allocated'] = total_allocated
        context['savings'] = savings
        context['over_budget'] = total_allocated > self.object.total_amount
        context['near_limit'] = total_allocated / self.object.total_amount > 0.8 if self.object.total_amount > 0 else False
        context['over_budget_amount'] = abs(savings) if savings < 0 else 0  # Calculate absolute value here
        context['chart_data'] = {
            'labels': [alloc.category for alloc in allocations] + (['Savings'] if savings > 0 else []),
            'data': [float(alloc.amount) for alloc in allocations] + ([float(savings)] if savings > 0 else []),
        }
        return context