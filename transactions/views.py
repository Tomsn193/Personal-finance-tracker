from locale import currency
import profile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime, timedelta, date
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
        
        # Update profile with selected currency
        profile, created = Profile.objects.get_or_create(
            user=user, 
            defaults={'currency': currency}
        )
        if not created:
            profile.currency = currency
            profile.save()
        
        # Create default categories
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
        
        messages.success(request, f'Account created successfully with {currency} currency! Please login.')
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
    period = request.GET.get('period', 'month')  # month, year, or all
    
    try:
        selected_year = int(request.GET.get('year', now.year))
        selected_month = int(request.GET.get('month', now.month))
    except ValueError:
        selected_year = now.year
        selected_month = now.month

    # Create a list of date objects for the dropdown
    months_list = [date(selected_year, m, 1) for m in range(1, 13)]
    
    # Get transactions based on selected period
    if period == 'month':
        transactions = Transaction.objects.filter(
            user=request.user,
            date__year=selected_year,
            date__month=selected_month
        ).order_by('-date')
        period_label = f"{months_list[selected_month - 1].strftime('%B %Y')}"
    elif period == 'year':
        transactions = Transaction.objects.filter(
            user=request.user,
            date__year=selected_year
        ).order_by('-date')
        period_label = f"{selected_year}"
    else:  # all
        transactions = Transaction.objects.filter(
            user=request.user
        ).order_by('-date')
        period_label = "All Time"
    
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
        year=selected_year,
        month=selected_month
    )
    
    # Get profile
    profile = get_object_or_404(Profile, user=request.user)
    
    # Recent transactions
    recent_transactions = transactions[:5]
    
    context = {
        'profile': profile,
        'currency': profile.currency,
        'balance': balance,
        'income': income,
        'expenses': expenses,
        'transactions': transactions,
        'recent_transactions': recent_transactions,
        'spending_by_category': spending_by_category,
        'budgets': budgets,
        'current_month': selected_month,
        'current_year': selected_year,
        'months': months_list,
        'years': range(now.year - 3, now.year + 1),
        'period': period,
        'period_label': period_label,
    }
    
    return render(request, 'dashboard.html', context)

# ============= Transaction Views =============

@login_required(login_url='login')
def transactions_list(request):
    """List all transactions"""
    # Start with all user transactions
    transactions = Transaction.objects.filter(user=request.user).order_by('-date')
    
    # Filter by category if selected
    category_id = request.GET.get('category')
    if category_id:
        transactions = transactions.filter(category_id=category_id)
    
    # Filter by type if selected
    transaction_type = request.GET.get('type')
    if transaction_type in ['income', 'expense']:
        transactions = transactions.filter(transaction_type=transaction_type)
    
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
        try:
            # Get form data
            amount_str = request.POST.get('amount', '0').strip()
            category_id = request.POST.get('category')
            description = request.POST.get('description', '').strip()
            transaction_type = request.POST.get('type')
            date_str = request.POST.get('date')
            
            # Validate amount exists and is not empty
            if not amount_str:
                messages.error(request, 'Please enter an amount')
                return redirect('add_transaction')
            
            # Try to convert to Decimal
            try:
                amount = Decimal(amount_str)
            except:
                messages.error(request, 'Invalid amount format. Please enter a valid number.')
                return redirect('add_transaction')
            
            # Validate amount is positive
            if amount <= 0:
                messages.error(request, 'Amount must be greater than 0')
                return redirect('add_transaction')
            
            # Validate amount is not too large (max 9999999.99)
            if amount > Decimal('9999999.99'):
                messages.error(request, 'Amount is too large. Maximum is 9,999,999.99')
                return redirect('add_transaction')
            
            # Validate amount has max 2 decimal places
            if amount.as_tuple().exponent < -2:
                messages.error(request, 'Amount can have maximum 2 decimal places')
                return redirect('add_transaction')
            
            # Validate category is selected
            if not category_id:
                messages.error(request, 'Please select a category')
                return redirect('add_transaction')
            
            # Validate transaction type
            if not transaction_type or transaction_type not in ['income', 'expense']:
                messages.error(request, 'Please select a valid transaction type')
                return redirect('add_transaction')
            
            # Get category and validate it belongs to user
            try:
                category = Category.objects.get(id=category_id, user=request.user)
            except Category.DoesNotExist:
                messages.error(request, 'Selected category does not exist')
                return redirect('add_transaction')
            
            # Validate category type matches transaction type
            if category.category_type != transaction_type:
                messages.error(request, f'Category must be an {transaction_type} category')
                return redirect('add_transaction')
            
            # Parse date if provided
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str)
                except:
                    messages.error(request, 'Invalid date format')
                    return redirect('add_transaction')
            else:
                date_obj = timezone.now()
            
            # Create transaction
            transaction = Transaction.objects.create(
                user=request.user,
                amount=amount,
                category=category,
                description=description,
                transaction_type=transaction_type,
                date=date_obj
            )
            
            messages.success(request, 'Transaction added successfully!')
            return redirect('transactions_list')
        
        except Exception as e:
            # Catch any unexpected errors
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('add_transaction')
    
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
        try:
            # Get form data
            amount_str = request.POST.get('amount', '0').strip()
            category_id = request.POST.get('category')
            description = request.POST.get('description', '').strip()
            transaction_type = request.POST.get('type')
            date_str = request.POST.get('date')
            
            # Validate amount
            if not amount_str:
                messages.error(request, 'Please enter an amount')
                return redirect('edit_transaction', pk=pk)
            
            try:
                amount = Decimal(amount_str)
            except:
                messages.error(request, 'Invalid amount format. Please enter a valid number.')
                return redirect('edit_transaction', pk=pk)
            
            if amount <= 0:
                messages.error(request, 'Amount must be greater than 0')
                return redirect('edit_transaction', pk=pk)
            
            if amount > Decimal('9999999.99'):
                messages.error(request, 'Amount is too large. Maximum is 9,999,999.99')
                return redirect('edit_transaction', pk=pk)
            
            if amount.as_tuple().exponent < -2:
                messages.error(request, 'Amount can have maximum 2 decimal places')
                return redirect('edit_transaction', pk=pk)
            
            # Validate category
            if not category_id:
                messages.error(request, 'Please select a category')
                return redirect('edit_transaction', pk=pk)
            
            try:
                category = Category.objects.get(id=category_id, user=request.user)
            except Category.DoesNotExist:
                messages.error(request, 'Selected category does not exist')
                return redirect('edit_transaction', pk=pk)
            
            if category.category_type != transaction_type:
                messages.error(request, f'Category must be an {transaction_type} category')
                return redirect('edit_transaction', pk=pk)
            
            # Parse date
            if date_str:
                try:
                    date_obj = datetime.fromisoformat(date_str)
                except:
                    messages.error(request, 'Invalid date format')
                    return redirect('edit_transaction', pk=pk)
            else:
                date_obj = timezone.now()
            
            # Update transaction
            transaction.amount = amount
            transaction.category = category
            transaction.description = description
            transaction.transaction_type = transaction_type
            transaction.date = date_obj
            transaction.save()
            
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transactions_list')
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('edit_transaction', pk=pk)
    
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
    # Get current month and year
    now = timezone.now()
    try:
        selected_year = int(request.GET.get('year', now.year))
        selected_month = int(request.GET.get('month', now.month))
    except ValueError:
        selected_year = now.year
        selected_month = now.month

    # Create a list of date objects for the dropdown
    months_list = [date(selected_year, m, 1) for m in range(1, 13)]
    
    profile = request.user.profile
    
    budgets = Budget.objects.filter(
        user=request.user,
        year=selected_year,
        month=selected_month
    )
    
    context = {
        'budgets': budgets,
        'currency': profile.currency,
        'current_month': selected_month,
        'current_year': selected_year,
        'months': months_list,
        'years': range(now.year - 1, now.year + 2),
    }
    
    return render(request, 'budgets.html', context)

@login_required(login_url='login')
def add_budget(request):
    """Add new budget"""
    if request.method == 'POST':
        try:
            category_id = request.POST.get('category')
            limit_str = request.POST.get('limit', '0').strip()
            year_str = request.POST.get('year')
            month_str = request.POST.get('month')
            
            # Validate category
            if not category_id:
                messages.error(request, 'Please select a category')
                return redirect('add_budget')
            
            # Validate limit
            if not limit_str:
                messages.error(request, 'Please enter a budget limit')
                return redirect('add_budget')
            
            try:
                limit = Decimal(limit_str)
            except:
                messages.error(request, 'Invalid budget limit. Please enter a valid number.')
                return redirect('add_budget')
            
            if limit <= 0:
                messages.error(request, 'Budget limit must be greater than 0')
                return redirect('add_budget')
            
            if limit > Decimal('9999999.99'):
                messages.error(request, 'Budget limit is too large. Maximum is 9,999,999.99')
                return redirect('add_budget')
            
            # Validate month and year
            try:
                month = int(month_str)
                year = int(year_str)
            except:
                messages.error(request, 'Invalid month or year')
                return redirect('add_budget')
            
            if month < 1 or month > 12:
                messages.error(request, 'Invalid month')
                return redirect('add_budget')
            
            # Get category
            try:
                category = Category.objects.get(id=category_id, user=request.user)
            except Category.DoesNotExist:
                messages.error(request, 'Selected category does not exist')
                return redirect('add_budget')
            
            # Check if budget already exists
            if Budget.objects.filter(
                user=request.user,
                category=category,
                year=year,
                month=month
            ).exists():
                messages.error(request, 'Budget for this category already exists for this month')
                return redirect('add_budget')
            
            # Create budget
            Budget.objects.create(
                user=request.user,
                category=category,
                limit=limit,
                year=year,
                month=month
            )
            
            messages.success(request, 'Budget added successfully!')
            return redirect('budgets')
        
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            return redirect('add_budget')
    
    now = timezone.now()
    categories = Category.objects.filter(user=request.user, category_type='expense')
    
    context = {
        'categories': categories,
        'years': range(now.year, now.year + 2),
        'months': range(1, 13),
        'current_month': now.month,
        'current_year': now.year,
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
    period = request.GET.get('period', 'month')  # month, year, or all
    
    # Parse year and month with error handling
    try:
        year = int(request.GET.get('year', now.year))
        month = int(request.GET.get('month', now.month))
    except (ValueError, TypeError):
        year = now.year
        month = now.month
    
    # Get transactions based on selected period
    if period == 'month':
        transactions = Transaction.objects.filter(
            user=request.user,
            date__year=year,
            date__month=month
        )
        period_label = f"{date(year, month, 1).strftime('%B %Y')}"
    elif period == 'year':
        transactions = Transaction.objects.filter(
            user=request.user,
            date__year=year
        )
        period_label = f"{year}"
    else:  # all
        transactions = Transaction.objects.filter(
            user=request.user
        )
        period_label = "All Time"
    
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
    
    # Calculate percentages
    if float(income) > 0:
        savings_rate = (float(income) - float(expenses)) / float(income) * 100
    else:
        savings_rate = 0
    
    profile = request.user.profile
    
    context = {
        'year': year,
        'month': month,
        'income': float(income),
        'expenses': float(expenses),
        'net': float(income) - float(expenses),
        'spending_by_category': spending_by_category,
        'currency': profile.currency,
        'savings_rate': round(savings_rate, 1),
        'years': range(now.year - 2, now.year + 1),
        'months': range(1, 13),
        'period': period,
        'period_label': period_label,
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