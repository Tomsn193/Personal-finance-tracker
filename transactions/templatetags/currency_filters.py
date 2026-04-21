from django import template
from transactions.currency import format_currency

register = template.Library()

@register.filter
def currency(amount, currency_code='USD'):
    """
    Template filter to format currency
    
    Usage in template:
    {{ amount|currency }}  -> uses default USD
    {{ amount|currency:"EUR" }}  -> uses EUR
    """
    return format_currency(amount, currency_code)

@register.filter
def currency_symbol(currency_code):
    """
    Get currency symbol
    
    Usage in template:
    {{ user.profile.currency|currency_symbol }}
    """
    from transactions.currency import CURRENCY_SYMBOLS
    return CURRENCY_SYMBOLS.get(currency_code, currency_code)