from django.shortcuts import render, get_object_or_404, redirect
from .forms import ProductForm
from django.contrib import messages
from products.models import Product
from orden.models import Orden

# Create your views here.

#GESTION DE PRODUCTOS
def listado_productos(request):
    productos = Product.objects.all()
    return render(request, 'gestion_productos/list_product.html',{
        'products': productos
    })

def agregar_producto(request):
    form = ProductForm()

    if request.method == 'POST':
        formulario = ProductForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Producto creado correctamente')
        else:
            form
            messages.error(request, 'No se creo correctamente el producto')
    
    return render (request, 'gestion_productos/agregar_product.html', {
        'productform' : form
    })

def modificar_producto(request, id):
    producto = get_object_or_404(Product, id=id)

    form = ProductForm(instance=producto)

    if request.method == 'POST':
        formulario = ProductForm(data=request.POST, instance=producto, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Producto editado correctamente')
            # return redirect('') redirigir al apartado que estan todos los productos agregados por el admin
        formulario


    return render(request, 'gestion_productos/editar_product.html',{
        'productForm' : form
    })

def eliminar_producto(request, id):
    producto = get_object_or_404(Product, id=id)
    producto.delete()
    return redirect('list_product_admin')

#GESTION DE PEDIDOS
def listado_ordenes(request):
    ordenes = Orden.objects.all().order_by('-fecha_pagada')
    return render(request, 'gestion_pedidos/list_ordenes.html',{
        'ordens' : ordenes
    })