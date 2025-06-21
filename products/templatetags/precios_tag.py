from django import template
from django.utils import timezone

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
    
@register.filter
def time_ago(value):
    # Convertir orden.fecha_pagada a la hora local
    hora_local = timezone.localtime(timezone.now())
    fecha_pagada_local = timezone.localtime(value)  # Convertimos orden.fecha_pagada a la hora local
    
    # Calcular la diferencia entre la hora local y la fecha de la orden
    diff = hora_local - fecha_pagada_local
    seconds = diff.total_seconds()
    
    # Comprobamos las diferencias de tiempo
    minutes = seconds // 60
    hours = minutes // 60
    days = hours // 24
    
    if days > 0:
        return f"Hace {int(days)} días"
    elif hours > 0:
        return f"Hace {int(hours)} horas"
    elif minutes > 0:
        return f"Hace {int(minutes)} minutos"
    else:
        return f"Hace {int(seconds)} segundos"