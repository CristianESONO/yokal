from django import template
from apps.loyalty.currency import CurrencyConverter

register = template.Library()


@register.filter
def format_currency(amount, currency_code):
    try:
        return CurrencyConverter.format_price(float(amount), currency_code)
    except Exception:
        return f"{amount} {currency_code}"


@register.filter
def to_currency(amount, currency_code):
    try:
        result = CurrencyConverter.convert(float(amount), 'XOF', currency_code)
        return f"{result:.2f}"
    except Exception:
        return amount


@register.filter
def add_symbol(amount, currency_code):
    symbols = {
        'XOF': 'FCFA',
        'EUR': '€',
        'USD': '$',
    }
    symbol = symbols.get(currency_code, currency_code)
    return f"{amount} {symbol}"


@register.simple_tag
def all_prices(amount, base_currency='XOF'):
    return CurrencyConverter.get_all_prices_formatted(float(amount), base_currency)


@register.simple_tag
def convert_price(amount, from_currency, to_currency):
    return CurrencyConverter.convert(float(amount), from_currency, to_currency)
