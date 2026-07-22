from django import template

register = template.Library()

@register.filter(name='replace_vars')
def replace_vars(value, card):
    if not value or not card:
        return value
    
    # Get logo URL with fallback to merchant logo
    logo_url = ''
    if card.program.logo:
        logo_url = card.program.logo.url
    elif card.program.merchant.logo:
        logo_url = card.program.merchant.logo.url
        
    replacements = {
        '{name}': card.customer_name,
        '{phone}': card.customer_phone or '',
        '{balance}': str(card.balance).split('.')[0], # Remove decimal for cleaner stamps
        '{total}': str(card.total_accumulated).split('.')[0],
        '{logo}': logo_url
    }
    
    for key, val in replacements.items():
        value = value.replace(key, str(val))
    
    return value
