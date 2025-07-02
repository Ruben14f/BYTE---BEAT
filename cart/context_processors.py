from .funciones import *

def carrito_context(request):
    cart = funcionCarrito(request)
    
    # Obtener los productos únicos en el carrito (sin contar la cantidad)
    productos_unicos = set(cart.product_related())
    
    # Contar el número de productos distintos
    cantidad_items = len(productos_unicos)
    
    return {
        'cart_items_count': cantidad_items,
    }