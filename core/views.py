from django.shortcuts import render
from products.models import Category
from orden.models import OrdenProducto
from django.db.models import Count
from profiles.models import UserProfile
from django.utils.timezone import now, localtime
from django.utils import formats
from orden.models import Orden
from django.db.models import Sum
from products.models import Product
from django.db.models.functions import TruncMonth

# Create your views here.
def index(request):
    category = Category.objects.annotate(product_count=Count('product')).filter(product_count__gt=0)

    mayor_vendido = OrdenProducto.total_productos_mas_vendido()


    return render(request, 'index.html',{
        'categoria' : category,
        'mas_vendido' : mayor_vendido
    })

def index_admin(request):
    profile = UserProfile.objects.get(user=request.user)
    hora_actual = localtime(now()).date() 
    dia_de_la_semana = formats.date_format(hora_actual, "l")
    # Obtener el total de precios de todas las órdenes
    total_precio_ordenes = Orden.objects.all().aggregate(Sum('total'))['total__sum']
    total_precio_ordenes = total_precio_ordenes if total_precio_ordenes else 0
    # Obtener el total de órdenes vendidas
    ordenes_totales_vendido = Orden.objects.all().count()

    #Obtener productos activos
    productos_activos = Product.objects.all().count()

    #5 productos mas vendidos
    mayor_vendido = OrdenProducto.total_productos_mas_vendido()
    
    # Obtener ventas mensuales
    ventas = ventas_mensuales()
    return render(request, 'index_admin.html', {
        'profile' : profile,
        'fecha_formateada': hora_actual,
        'dia_de_la_semana': dia_de_la_semana,
        'total_ventas_pesos': total_precio_ordenes,
        'total_ventas_cantidad': ordenes_totales_vendido,
        'productos_activos': productos_activos,
        'mas_vendido': mayor_vendido,
        'ventas_mensuales': ventas
    })


def ventas_mensuales():
    ventas = (
        Orden.objects
        .annotate(mes=TruncMonth('fecha_pagada'))  
        .values('mes')
        .annotate(total_ventas=Sum('total'))  
        .order_by('mes')  
    )
    return ventas