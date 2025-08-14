from django.urls import path
from . import views

app_name = 'finance'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('income/create/', views.IncomeCreateView.as_view(), name='income_create'),
    path('budget/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budget/<int:pk>/', views.BudgetDetailView.as_view(), name='budget_detail'),
    path('budget/<int:budget_id>/allocate/', views.AllocationCreateView.as_view(), name='allocation_create'),
    path('get-total-income/', views.get_total_income, name='get_total_income'),
]