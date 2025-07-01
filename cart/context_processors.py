from .funciones import *

def carrito_context(request):
    cart = funcionCarrito(request)
    cantidad_items = sum([item.quantity for item in cart.product_related()])
    
    return {
        'cart_items_count': cantidad_items,
    }