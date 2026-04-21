from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile, Category, Transaction, Budget


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for User Profile"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Profile
        fields = ['id', 'user', 'currency']
        read_only_fields = ['id', 'user']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    class Meta:
        model = Category
        fields = ['id', 'user', 'name', 'category_type', 'color', 'icon', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for Transaction model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'amount', 'category', 'category_name', 
            'description', 'transaction_type', 'date', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budget model"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Budget
        fields = [
            'id', 'user', 'category', 'category_name', 
            'limit', 'year', 'month', 'created_at'
        ]
        read_only_fields = ['id', 'user', 'created_at']


class DashboardSummarySerializer(serializers.Serializer):
    """Serializer for dashboard summary data"""
    period = serializers.CharField()
    period_label = serializers.CharField()
    income = serializers.DecimalField(max_digits=10, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    currency = serializers.CharField()
    transaction_count = serializers.IntegerField()
    spending_by_category = serializers.DictField()


class ReportSummarySerializer(serializers.Serializer):
    """Serializer for report summary data"""
    period = serializers.CharField()
    period_label = serializers.CharField()
    income = serializers.DecimalField(max_digits=10, decimal_places=2)
    expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    net = serializers.DecimalField(max_digits=10, decimal_places=2)
    savings_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    currency = serializers.CharField()
    spending_by_category = serializers.DictField()