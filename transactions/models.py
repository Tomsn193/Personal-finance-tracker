# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User


class Profile(models.Model):
    """Extended user profile"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currency = models.CharField(max_length=3, default='USD')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_balance(self):
        """Calculate current balance"""
        transactions = self.user.transactions.all()
        return sum(float(t.amount) if t.transaction_type == 'income' else -float(t.amount) 
                  for t in transactions)

class Category(models.Model):
    """Transaction categories"""
    CATEGORY_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=10, choices=CATEGORY_TYPES)
    color = models.CharField(max_length=7, default='#3498db')
    icon = models.CharField(max_length=50, default='money')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category_type', 'name']
        unique_together = ('user', 'name', 'category_type')
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"

class Transaction(models.Model):
    """Financial transactions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=200, blank=True)
    transaction_type = models.CharField(
        max_length=10,
        choices=[('income', 'Income'), ('expense', 'Expense')],
        default='expense'
    )
    date = models.DateTimeField(default=timezone.now)
    tags = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', '-date']),
            models.Index(fields=['user', 'category']),
        ]
    
    def __str__(self):
        sign = '+' if self.transaction_type == 'income' else '-'
        return f"{sign}${self.amount} - {self.category} ({self.date.strftime('%Y-%m-%d')})"

class Budget(models.Model):
    """Monthly budgets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    year = models.IntegerField()
    month = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'category', 'year', 'month')
        ordering = ['-year', '-month']
    
    def __str__(self):
        return f"{self.category.name} - ${self.limit} ({self.month}/{self.year})"
    
    def get_spent(self):
        """Get amount spent in this budget period"""
        transactions = self.user.transactions.filter(
            category=self.category,
            transaction_type='expense',
            date__year=self.year,
            date__month=self.month
        )
        total = sum(float(t.amount) for t in transactions)
        return total
    
    def get_percentage(self):
        """Get spending percentage of budget"""
        spent = self.get_spent()
        if self.limit == 0:
            return 0
        return min(100, int((spent / self.limit) * 100))
    
    def is_over_budget(self):
        """Check if over budget"""
        return self.get_spent() > self.limit
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()