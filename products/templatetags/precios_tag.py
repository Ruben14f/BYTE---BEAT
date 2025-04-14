from django import template

register = template.Library()

@register.filter
def format_price(value):
    """
    Formatea el valor como precio con separadores de miles y símbolo de moneda.
    Ejemplo: 213021 se convierte en $213.021
    """
    try:
        # Asegúrate de que el valor sea un número
        value = float(value)
        return '${:,.0f}'.format(value).replace(',', '.')
    except (ValueError, TypeError):
        return value  # Devuelve el valor original si no se puede formatear