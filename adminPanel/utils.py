from orden.models import Orden
from products.models import Product
from django.db.models import Sum
from django.utils import timezone


#Ordenes completadas y entregadas
def total_pedidos_hoy():
    hoy = timezone.localtime(timezone.now()).date() 
    print(hoy)
    ordenes_totales = Orden.objects.exclude(status='CREATED').filter(fecha_pagada__date=hoy).count() 
    print(ordenes_totales)
    return ordenes_totales

#Ordenes completadas y entregadas
def total_pedidos_completados():
    ordenes_completadas = Orden.objects.filter(status='DELIVERED').count()
    return ordenes_completadas

#Para admin-index y list_ordenes
def ingresos_totales():
    total_precio_ordenes = Orden.objects.filter(status='DELIVERED').aggregate(Sum('total'))['total__sum']
    total_precio_ordenes = total_precio_ordenes if total_precio_ordenes else 0
    return total_precio_ordenes

def total_ordenes():
    ordenes_totales = Orden.objects.exclude(status='CREATED').count()
    return ordenes_totales

"""
Funciones:
- total_productos
- total_productos_activos
- productos_stock_bajo

Son para list_product
"""
def total_productos():
    total_productos =Product.objects.count()
    return total_productos

def total_productos_activos():
    total_productos_activos = Product.objects.filter(status='ACTIVE').count()
    return total_productos_activos

def productos_stock_bajo():
    productos_stock_bajo = Product.objects.filter(stock__lte=5, status='ACTIVE').count()
    return productos_stock_bajo

def productos_sin_stock():
    productos_sin_stock = Product.objects.filter(status='INACTIVE').count()
    return productos_sin_stock