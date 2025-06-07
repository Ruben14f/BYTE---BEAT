from django.shortcuts import render
from products.models import Product
from orden.models import Orden
from django.utils.safestring import mark_safe


def consulta_stock(sku: str) -> str:
    try:
        # Busca el producto con el SKU proporcionado
        product = Product.objects.get(sku=sku)
        # Si se encuentra el producto, devuelve el stock
        return mark_safe(f"El stock disponible para el SKU {sku} es {product.stock}.")
    except Product.DoesNotExist:
        # Si no se encuentra el producto, muestra un mensaje
        return mark_safe("El producto con el SKU proporcionado no existe en la tienda.")

def consultar_estado_pedido(num_orden: str) -> str:
    try:
        # Buscar la orden 
        orden = Orden.objects.get(num_orden=num_orden)
        # Si se encuentra la orden, devuelve el estado
        return mark_safe(f"El estado de la orden {num_orden} es {orden.status}.")
    except Product.DoesNotExist:
        # Si no se encuentra la orden, muestra un mensaje
        return mark_safe("La orden no se encuentra en el sistema")
    