
# pesa_plan/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  
    path('', include('finance.urls')),  # Finance app URLs
]