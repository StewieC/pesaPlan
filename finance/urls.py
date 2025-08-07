from django.urls import path
from . import views
from django.urls import reverse_lazy

app_name = 'finance'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('budget/create/', views.BudgetCreateView.as_view(), name='budget_create'),
    path('budget/<int:budget_id>/allocate/', views.AllocationCreateView.as_view(), name='allocation_create'),
    path('budget/<int:pk>/', views.BudgetDetailView.as_view(), name='budget_detail'),
]