from locale import currency

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from .models import Profile, Category, Transaction, Budget

# ============= Authentication Views =============

def register(request):
    """User registration"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        currency = request.POST.get('currency', 'USD')
        
        if password != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')
        
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)

        user.profile.currency = currency
        user.profile.save()
        
        income_cat = Category.objects.create(
            user=user,
            name='Salary',
            category_type='income',
            color='#27ae60',
            icon='dollar'
        )
        
        categories = [
            ('Food', 'expense', '#e74c3c'),
            ('Transport', 'expense', '#3498db'),
            ('Entertainment', 'expense', '#9b59b6'),
            ('Utilities', 'expense', '#f39c12'),
            ('Shopping', 'expense', '#1abc9c'),
            ('Health', 'expense', '#e67e22'),
        ]
        
        for name, cat_type, color in categories:
            Category.objects.create(
                user=user,
                name=name,
                category_type=cat_type,
                color=color
            )
        
        messages.success(request, 'Account created successfully! Please login.')
        return redirect('login')
    
    return render(request, 'register.html')

def login_view(request):
    """User login"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def logout_view(request):
    """User logout"""
    logout(request)
    return redirect('login')

# ============= Dashboard Views =============

@login_required(login_url='login')
def dashboard(request):
    """Main dashboard"""
    # Get current month and year
    now = timezone.now()
    year = request.GET.get('year', now.year)
    month = request.GET.get('month', now.month)
    
    # Get all transactions for current month
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    ).order_by('-date')
    
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
            spending_by_category[cat_name] = {
                'amount': 0,
                'color': trans.category.color if trans.category else '#95a5a6'
            }
        spending_by_category[cat_name]['amount'] += float(trans.amount)
    
    # Get budgets
    budgets = Budget.objects.filter(
        user=request.user,
        year=year,
        month=month
    )
    
    # Get profile
    profile = get_object_or_404(Profile, user=request.user)
    
    # Recent transactions
    recent_transactions = transactions[:5]
    
    context = {
        'profile': profile,
        'balance': balance,
        'income': income,
        'expenses': expenses,
        'transactions': transactions,
        'recent_transactions': recent_transactions,
        'spending_by_category': spending_by_category,
        'budgets': budgets,
        'current_month': int(month),
        'current_year': int(year),
        'months': range(1, 13),
        'years': range(now.year - 3, now.year + 1),
        'currency': profile.currency,
    }
    
    return render(request, 'dashboard.html', context)

# ============= Transaction Views =============

@login_required(login_url='login')
def transactions_list(request):
    """List all transactions"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    categories = Category.objects.filter(user=request.user)
    profile = request.user.profile
    context = {
        'transactions': transactions,
        'categories': categories,
        'currency': profile.currency,
    }
    
    return render(request, 'transactions_list.html', context)

@login_required(login_url='login')
def add_transaction(request):
    """Add new transaction"""
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        transaction_type = request.POST.get('type')
        date_str = request.POST.get('date')
        
        if amount <= 0:
            messages.error(request, 'Amount must be greater than 0')
            return redirect('add_transaction')
        
        category = get_object_or_404(Category, id=category_id, user=request.user)
        
        if date_str:
            date = datetime.fromisoformat(date_str)
        else:
            date = timezone.now()
        
        transaction = Transaction.objects.create(
            user=request.user,
            amount=amount,
            category=category,
            description=description,
            transaction_type=transaction_type,
            date=date
        )
        
        messages.success(request, 'Transaction added successfully!')
        return redirect('transactions_list')
    
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'add_transaction.html', context)

@login_required(login_url='login')
def edit_transaction(request, pk):
    """Edit transaction"""
    transaction = get_object_or_404(Transaction, id=pk, user=request.user)
    
    if request.method == 'POST':
        transaction.amount = Decimal(request.POST.get('amount'))
        transaction.category_id = request.POST.get('category')
        transaction.description = request.POST.get('description')
        transaction.transaction_type = request.POST.get('type')
        
        date_str = request.POST.get('date')
        if date_str:
            transaction.date = datetime.fromisoformat(date_str)
        
        transaction.save()
        
        messages.success(request, 'Transaction updated successfully!')
        return redirect('transactions_list')
    
    categories = Category.objects.filter(user=request.user)
    
    context = {
        'transaction': transaction,
        'categories': categories,
    }
    
    return render(request, 'edit_transaction.html', context)

@login_required(login_url='login')
def delete_transaction(request, pk):
    """Delete transaction"""
    transaction = get_object_or_404(Transaction, id=pk, user=request.user)
    
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, 'Transaction deleted successfully!')
        return redirect('transactions_list')
    
    context = {
        'transaction': transaction,
    }
    
    return render(request, 'delete_transaction.html', context)

# ============= Category Views =============

@login_required(login_url='login')
def categories(request):
    """List categories"""
    income_categories = Category.objects.filter(user=request.user, category_type='income')
    expense_categories = Category.objects.filter(user=request.user, category_type='expense')
    
    context = {
        'income_categories': income_categories,
        'expense_categories': expense_categories,
    }
    
    return render(request, 'categories.html', context)

@login_required(login_url='login')
def add_category(request):
    """Add new category"""
    if request.method == 'POST':
        name = request.POST.get('name')
        category_type = request.POST.get('type')
        color = request.POST.get('color', '#3498db')
        
        if Category.objects.filter(user=request.user, name=name, category_type=category_type).exists():
            messages.error(request, 'This category already exists')
            return redirect('add_category')
        
        Category.objects.create(
            user=request.user,
            name=name,
            category_type=category_type,
            color=color
        )
        
        messages.success(request, 'Category added successfully!')
        return redirect('categories')
    
    return render(request, 'add_category.html')

@login_required(login_url='login')
def delete_category(request, pk):
    """Delete category"""
    category = get_object_or_404(Category, id=pk, user=request.user)
    
    # Check if category is used
    if Transaction.objects.filter(category=category).exists():
        messages.error(request, 'Cannot delete category that has transactions')
        return redirect('categories')
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Category deleted successfully!')
        return redirect('categories')
    
    context = {
        'category': category,
    }
    
    return render(request, 'delete_category.html', context)

# ============= Budget Views =============

@login_required(login_url='login')
def budgets(request):
    """List budgets"""
    now = timezone.now()
    year = request.GET.get('year', now.year)
    month = request.GET.get('month', now.month)
    
    budgets = Budget.objects.filter(
        user=request.user,
        year=year,
        month=month
    )
    profile = request.user.profile
    context = {
        'budgets': budgets,
        'current_month': int(month),
        'current_year': int(year),
        'months': range(1, 13),
        'years': range(now.year - 1, now.year + 2),
        'currency': profile.currency,
    }
    
    return render(request, 'budgets.html', context)

@login_required(login_url='login')
def add_budget(request):
    """Add new budget"""
    if request.method == 'POST':
        category_id = request.POST.get('category')
        limit = Decimal(request.POST.get('limit'))
        year = int(request.POST.get('year'))
        month = int(request.POST.get('month'))
        
        category = get_object_or_404(Category, id=category_id, user=request.user)
        
        if Budget.objects.filter(
            user=request.user,
            category=category,
            year=year,
            month=month
        ).exists():
            messages.error(request, 'Budget for this category already exists')
            return redirect('add_budget')
        
        Budget.objects.create(
            user=request.user,
            category=category,
            limit=limit,
            year=year,
            month=month
        )
        
        messages.success(request, 'Budget added successfully!')
        return redirect('budgets')
    
    now = timezone.now()
    categories = Category.objects.filter(user=request.user, category_type='expense')
    
    context = {
        'categories': categories,
        'years': range(now.year, now.year + 2),
        'months': range(1, 13),
    }
    
    return render(request, 'add_budget.html', context)

@login_required(login_url='login')
def delete_budget(request, pk):
    """Delete budget"""
    budget = get_object_or_404(Budget, id=pk, user=request.user)
    
    if request.method == 'POST':
        budget.delete()
        messages.success(request, 'Budget deleted successfully!')
        return redirect('budgets')
    
    context = {
        'budget': budget,
    }
    
    return render(request, 'delete_budget.html', context)

# ============= Reports Views =============

@login_required(login_url='login')
def reports(request):
    """Financial reports"""
    now = timezone.now()
    year = int(request.GET.get('year', now.year))
    month = int(request.GET.get('month', now.month))
    
    # Monthly summary
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    )
    
    income = transactions.filter(transaction_type='income').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    expenses = transactions.filter(transaction_type='expense').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    # Spending by category
    spending_by_category = {}
    for trans in transactions.filter(transaction_type='expense'):
        cat_name = trans.category.name if trans.category else 'Uncategorized'
        if cat_name not in spending_by_category:
            spending_by_category[cat_name] = 0
        spending_by_category[cat_name] += float(trans.amount)
    
    spending_by_category = dict(sorted(
        spending_by_category.items(),
        key=lambda x: x[1],
        reverse=True
    ))
    profile = request.user.profile
    context = {
        'year': year,
        'month': month,
        'income': float(income),
        'expenses': float(expenses),
        'net': float(income) - float(expenses),
        'spending_by_category': spending_by_category,
        'years': range(now.year - 2, now.year + 1),
        'months': range(1, 13),
        'currency': profile.currency,
    }
    
    return render(request, 'reports.html', context)

# ============= Settings Views =============

@login_required(login_url='login')
def settings(request):
    """User settings"""
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        profile.currency = request.POST.get('currency', 'USD')
        profile.save()
        
        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')
    
    context = {
        'profile': profile,
        'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD', 'JPY', 'INR', 'ZAR', 'NGN'],
    }
    
    return render(request, 'settings.html', context)