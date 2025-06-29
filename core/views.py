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
from adminPanel.utils import ingresos_totales
from adminPanel.utils import *
import os
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required




def tests(request):
    return render(request, 'testdesign.html')
    
# Create your views here.
def index(request):
    category = Category.objects.annotate(product_count=Count('product')).filter(product_count__gt=0)

    mayor_vendido = OrdenProducto.total_productos_mas_vendido()
    return render(request, 'index.html',{
        'categoria' : category,
        'mas_vendido' : mayor_vendido
    })

@staff_member_required(login_url='/')
def index_admin(request):
    profile = UserProfile.objects.get(user=request.user)
    
    hora_actual = localtime(now()).date() 
    dia_de_la_semana = formats.date_format(hora_actual, "l")


    # Obtener el total de precios de todas las ordenes
    total_precio_ordenes = ingresos_totales()


    # Obtener el total de órdenes vendidas
    ordenes_totales_vendido = total_ordenes()

    #Obtener productos activos
    productos_activos = Product.objects.all().count()

    #5 productos mas vendidos
    mayor_vendido = OrdenProducto.total_productos_mas_vendido()
    
    # Obtener ventas mensuales
    ventas = ventas_mensuales()

    #10 Ordenes recientes
    ordenes_recientes = Orden.ordenes_recentes(limite=10)

    return render(request, 'index_admin.html', {
        'profile' : profile,
        'fecha_formateada': hora_actual,
        'dia_de_la_semana': dia_de_la_semana,
        'total_ventas_pesos': total_precio_ordenes,
        'total_ventas_cantidad': ordenes_totales_vendido,
        'productos_activos': productos_activos,
        'mas_vendido': mayor_vendido,
        'ventas_mensuales': ventas,
        'ordenes_recientes': ordenes_recientes
    })

def form_contacto(request):
    if request.method == 'POST':
        # Extrae los datos del formulario
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        tipoConsulta = request.POST.get('tipoConsulta')
        asunto = request.POST.get('asunto')
        mensaje = request.POST.get('mensaje')

        # Verifica si el usuario está autenticado
        if request.user.is_authenticated:
            email = request.user.email

        # Llamar a la función correo_de_contacto para enviar el correo
        correo_de_contacto(nombres, apellidos, email, telefono, tipoConsulta, asunto, mensaje)

        # Mostrar mensaje de éxito
        messages.success(request, 'Mensaje enviado. Te responderemos pronto.')
        return render(request, 'formulario_contacto.html')

    return render(request, 'formulario_contacto.html')

# Función para enviar el correo

def correo_de_contacto(nombres, apellidos, email, telefono, tipoConsulta, asunto, mensaje):
    email_host = os.environ.get('EMAIL_HOST_USER')  # Usando variable de entorno para obtener el correo del servidor

    # Construir el mensaje HTML
    html_message = f"""
    <h3>Detalles del mensaje:</h3>
    <p><strong>Nombre:</strong> {nombres} {apellidos}</p>
    <p><strong>Email:</strong> {email}</p>
    <p><strong>Teléfono:</strong> {telefono}</p>
    <p><strong>Tipo de consulta:</strong> {tipoConsulta}</p>
    <p><strong>Asunto:</strong> {asunto}</p>
    <p><strong>Mensaje:</strong> {mensaje}</p>
    """

    try:
        send_mail(
            'Consulta de Contacto',
            'Detalles de la consulta recibida.',
            from_email=email_host, 
            recipient_list=[email_host],  # Dirección a la que deseas enviar el correo
            fail_silently=False,
            html_message=html_message
        )
        print('Correo enviado con éxito')
    except Exception as e:
        print('Error al enviar correo:', e)

def ventas_mensuales():
    ventas = (
        Orden.objects
        .annotate(mes=TruncMonth('fecha_pagada'))  
        .values('mes')
        .annotate(total_ventas=Sum('total'))  
        .filter(status='DELIVERED')
        .order_by('mes') 
    )
    return ventas