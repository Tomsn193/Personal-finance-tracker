from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from django.utils import timezone
from datetime import date
import json

from .models import Profile, Category, Transaction, Budget
from .serializers import (
    ProfileSerializer, CategorySerializer, TransactionSerializer,
    BudgetSerializer, DashboardSummarySerializer, ReportSummarySerializer
)


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user profile management.
    
    Usage:
    - GET /api/profile/ - Get current user's profile
    - PUT /api/profile/{id}/ - Update profile
    - PATCH /api/profile/{id}/ - Partial update
    """
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only return current user's profile"""
        return Profile.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CategoryViewSet(viewsets.ModelViewSet):
    """
    API endpoint for category management.
    
    Usage:
    - GET /api/categories/ - List all categories
    - POST /api/categories/ - Create category
    - GET /api/categories/{id}/ - Get category details
    - PUT /api/categories/{id}/ - Update category
    - DELETE /api/categories/{id}/ - Delete category
    """
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only return current user's categories"""
        return Category.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def income_categories(self, request):
        """Get only income categories"""
        categories = Category.objects.filter(
            user=request.user,
            category_type='income'
        )
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expense_categories(self, request):
        """Get only expense categories"""
        categories = Category.objects.filter(
            user=request.user,
            category_type='expense'
        )
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class TransactionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for transaction management.
    
    Usage:
    - GET /api/transactions/ - List all transactions
    - POST /api/transactions/ - Create transaction
    - GET /api/transactions/{id}/ - Get transaction details
    - PUT /api/transactions/{id}/ - Update transaction
    - DELETE /api/transactions/{id}/ - Delete transaction
    
    Filters:
    - /api/transactions/?category=1 - Filter by category
    - /api/transactions/?type=income - Filter by type
    - /api/transactions/?month=4&year=2026 - Filter by month/year
    """
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get current user's transactions with optional filtering"""
        queryset = Transaction.objects.filter(user=self.request.user).order_by('-date')
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        
        # Filter by type
        trans_type = self.request.query_params.get('type')
        if trans_type in ['income', 'expense']:
            queryset = queryset.filter(transaction_type=trans_type)
        
        # Filter by month/year
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(
                date__year=int(year),
                date__month=int(month)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get transaction summary for a period.
        
        Query params:
        - period: 'month', 'year', or 'all' (default: 'month')
        - month: month number (1-12)
        - year: year number
        
        Example: /api/transactions/summary/?period=year&year=2026
        """
        period = request.query_params.get('period', 'month')
        
        try:
            month = int(request.query_params.get('month', timezone.now().month))
            year = int(request.query_params.get('year', timezone.now().year))
        except ValueError:
            month = timezone.now().month
            year = timezone.now().year
        
        # Filter transactions by period
        if period == 'month':
            transactions = Transaction.objects.filter(
                user=request.user,
                date__year=year,
                date__month=month
            )
            period_label = date(year, month, 1).strftime('%B %Y')
        elif period == 'year':
            transactions = Transaction.objects.filter(
                user=request.user,
                date__year=year
            )
            period_label = str(year)
        else:  # all
            transactions = Transaction.objects.filter(user=request.user)
            period_label = 'All Time'
        
        # Calculate statistics
        income = transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        expenses = transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        balance = float(income) - float(expenses)
        
        # Get spending by category
        spending_by_category = {}
        for trans in transactions.filter(transaction_type='expense'):
            cat_name = trans.category.name if trans.category else 'Uncategorized'
            if cat_name not in spending_by_category:
                spending_by_category[cat_name] = 0
            spending_by_category[cat_name] += float(trans.amount)
        
        profile = request.user.profile
        
        data = {
            'period': period,
            'period_label': period_label,
            'income': float(income),
            'expenses': float(expenses),
            'balance': balance,
            'currency': profile.currency,
            'transaction_count': transactions.count(),
            'spending_by_category': spending_by_category,
        }
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get transactions grouped by category.
        
        Example: /api/transactions/by_category/?type=expense
        """
        trans_type = request.query_params.get('type')
        
        if trans_type:
            transactions = Transaction.objects.filter(
                user=request.user,
                transaction_type=trans_type
            )
        else:
            transactions = Transaction.objects.filter(user=request.user)
        
        # Group by category
        grouped = {}
        for trans in transactions:
            cat_name = trans.category.name if trans.category else 'Uncategorized'
            if cat_name not in grouped:
                grouped[cat_name] = []
            grouped[cat_name].append({
                'id': trans.id,
                'amount': str(trans.amount),
                'date': trans.date,
                'description': trans.description,
            })
        
        return Response(grouped)


class BudgetViewSet(viewsets.ModelViewSet):
    """
    API endpoint for budget management.
    
    Usage:
    - GET /api/budgets/ - List all budgets
    - POST /api/budgets/ - Create budget
    - GET /api/budgets/{id}/ - Get budget details
    - PUT /api/budgets/{id}/ - Update budget
    - DELETE /api/budgets/{id}/ - Delete budget
    
    Filters:
    - /api/budgets/?month=4&year=2026 - Filter by month/year
    """
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get current user's budgets with optional filtering"""
        queryset = Budget.objects.filter(user=self.request.user)
        
        # Filter by month/year
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(
                month=int(month),
                year=int(year)
            )
        
        return queryset.order_by('-year', '-month')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Get budget status with spending comparison.
        
        Query params:
        - month: month number (1-12)
        - year: year number
        
        Example: /api/budgets/status/?month=4&year=2026
        """
        try:
            month = int(request.query_params.get('month', timezone.now().month))
            year = int(request.query_params.get('year', timezone.now().year))
        except ValueError:
            month = timezone.now().month
            year = timezone.now().year
        
        budgets = Budget.objects.filter(
            user=request.user,
            month=month,
            year=year
        )
        
        budget_status = []
        for budget in budgets:
            # Get spending for this category in this month
            spending = Transaction.objects.filter(
                user=request.user,
                category=budget.category,
                date__year=year,
                date__month=month,
                transaction_type='expense'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            remaining = float(budget.limit) - float(spending)
            percentage = (float(spending) / float(budget.limit) * 100) if budget.limit > 0 else 0
            
            budget_status.append({
                'budget_id': budget.id,
                'category': budget.category.name,
                'limit': str(budget.limit),
                'spent': str(spending),
                'remaining': str(remaining),
                'percentage': round(percentage, 2),
                'status': 'on_track' if remaining >= 0 else 'exceeded',
            })
        
        return Response({
            'month': month,
            'year': year,
            'budgets': budget_status,
            'total_budgeted': str(sum(float(b['limit']) for b in budget_status)),
            'total_spent': str(sum(float(b['spent']) for b in budget_status)),
        })


class DashboardViewSet(viewsets.ViewSet):
    """
    API endpoint for dashboard data.
    
    Usage:
    - GET /api/dashboard/?period=month&month=4&year=2026 - Get dashboard summary
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get complete dashboard summary"""
        period = request.query_params.get('period', 'month')
        
        try:
            month = int(request.query_params.get('month', timezone.now().month))
            year = int(request.query_params.get('year', timezone.now().year))
        except ValueError:
            month = timezone.now().month
            year = timezone.now().year
        
        # Get transactions based on period
        if period == 'month':
            transactions = Transaction.objects.filter(
                user=request.user,
                date__year=year,
                date__month=month
            )
            period_label = date(year, month, 1).strftime('%B %Y')
        elif period == 'year':
            transactions = Transaction.objects.filter(
                user=request.user,
                date__year=year
            )
            period_label = str(year)
        else:  # all
            transactions = Transaction.objects.filter(user=request.user)
            period_label = 'All Time'
        
        # Calculate statistics
        income = transactions.filter(transaction_type='income').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        expenses = transactions.filter(transaction_type='expense').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        balance = float(income) - float(expenses)
        
        # Get spending by category
        spending_by_category = {}
        for trans in transactions.filter(transaction_type='expense'):
            cat_name = trans.category.name if trans.category else 'Uncategorized'
            if cat_name not in spending_by_category:
                spending_by_category[cat_name] = {'amount': 0, 'color': '#95a5a6'}
            spending_by_category[cat_name]['amount'] += float(trans.amount)
            if trans.category:
                spending_by_category[cat_name]['color'] = trans.category.color
        
        profile = request.user.profile
        
        return Response({
            'period': period,
            'period_label': period_label,
            'income': str(income),
            'expenses': str(expenses),
            'balance': balance,
            'currency': profile.currency,
            'transaction_count': transactions.count(),
            'recent_transactions': TransactionSerializer(
                transactions[:5], many=True
            ).data,
            'spending_by_category': spending_by_category,
            'month': month,
            'year': year,
        })