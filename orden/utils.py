
from .models import Orden
from django.urls import reverse

def funcionOrden(cart,request):
    orden = cart.orden

    if orden is None and request.user.is_authenticated:
        orden = Orden.objects.create(cart=cart, user=request.user)

    if orden:
        request.session['orden_id'] = orden.id    
    
    return orden

def breadcrumb(Cart=False, products=False, confirmation=False):
    return[
        {'title' : 'Carrito', 'active':Cart, 'url': reverse('cart')},
        {'title' : 'Productos', 'active':products, 'url': reverse('orden')},
        {'title' : 'Confirmacion', 'active':confirmation, 'url': reverse('orden')},
    ]