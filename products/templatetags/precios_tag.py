from django import template

register = template.Library()

@register.filter
def format_price(value):

    try:
        # Asegúrate de que el valor sea un número
        value = float(value)
        return '${:,.0f}'.format(value).replace(',', '.')
    except (ValueError, TypeError):
        return value  # Devuelve el valor original si no se puede formatear
    
@register.filter
def format_miles(value):

    try:
        # Asegúrate de que el valor sea un número
        value = float(value)
        return '{:,.0f}'.format(value).replace(',', '.')
    except (ValueError, TypeError):
        return value  # Devuelve el valor original si no se puede formatear