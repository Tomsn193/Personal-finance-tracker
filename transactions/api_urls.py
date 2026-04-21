from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import (
    ProfileViewSet, CategoryViewSet, TransactionViewSet,
    BudgetViewSet, DashboardViewSet
)

# Create router for API endpoints
router = DefaultRouter()
router.register(r'profile', ProfileViewSet, basename='profile')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r'budgets', BudgetViewSet, basename='budget')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]