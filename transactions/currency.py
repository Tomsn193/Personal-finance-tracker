# Currency formatting utilities

CURRENCY_SYMBOLS = {
    'USD': '$',
    'EUR': '€',
    'GBP': '£',
    'JPY': '¥',
    'AUD': 'A$',
    'CAD': 'C$',
    'CHF': 'CHF',
    'CNY': '¥',
    'INR': '₹',
    'MXN': '$',
    'SGD': 'S$',
    'ZAR': 'R',
    'NGN': '₦',
}

CURRENCY_NAMES = {
    'USD': 'US Dollar',
    'EUR': 'Euro',
    'GBP': 'British Pound',
    'JPY': 'Japanese Yen',
    'AUD': 'Australian Dollar',
    'CAD': 'Canadian Dollar',
    'CHF': 'Swiss Franc',
    'CNY': 'Chinese Yuan',
    'INR': 'Indian Rupee',
    'MXN': 'Mexican Peso',
    'SGD': 'Singapore Dollar',
    'ZAR': 'South African Rand',
    'NGN': 'Nigerian Naira',
}

def format_currency(amount, currency='USD'):
    """
    Format amount with currency symbol
    
    Args:
        amount: Decimal or float amount
        currency: Currency code (e.g., 'USD', 'EUR')
    
    Returns:
        Formatted string like '$1,234.56' or '€1.234,56'
    """
    if not amount:
        amount = 0
    
    amount = float(amount)
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    
    # Format with thousands separator
    if currency == 'EUR':
        # European style: 1.234,56
        return f"{symbol}{amount:,.2f}".replace(',', '_').replace('.', ',').replace('_', '.')
    else:
        # US/Most countries style: $1,234.56
        return f"{symbol}{amount:,.2f}"

def get_currency_info(currency='USD'):
    """Get currency symbol and name"""
    return {
        'code': currency,
        'symbol': CURRENCY_SYMBOLS.get(currency, currency),
        'name': CURRENCY_NAMES.get(currency, currency),
    }

def get_user_currency(user):
    """Get user's preferred currency"""
    try:
        return user.profile.currency
    except:
        return 'USD'