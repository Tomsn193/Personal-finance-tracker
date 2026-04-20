from django.contrib import admin

# Register your models here.
from .models import Profile, Category, Transaction, Budget

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'currency', 'created_at')
    readonly_fields = ('created_at',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'category_type', 'created_at')
    list_filter = ('category_type', 'created_at')
    search_fields = ('name', 'user__username')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'category', 'transaction_type', 'date')
    list_filter = ('transaction_type', 'category', 'date')
    search_fields = ('description', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'date'

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'limit', 'month', 'year')
    list_filter = ('year', 'month')
    search_fields = ('user__username', 'category__name')