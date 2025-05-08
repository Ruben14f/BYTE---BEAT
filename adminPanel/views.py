from django.shortcuts import render, get_object_or_404, redirect
from .forms import ProductForm
from django.contrib import messages
from products.models import Product
from orden.models import Orden, OrdenStatus
from django.db.models import Q
# Create your views here.

#GESTION DE PRODUCTOS
def listado_productos(request):
    productos = Product.objects.all()
    orden_status = OrdenStatus.choices
    print('estados disponible', orden_status)
    return render(request, 'gestion_productos/list_product.html',{
        'products': productos,
        'statusorden' : orden_status
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

def orden_search(request):
    query = request.GET.get('searchOrden')
    if query:
        filter = Q(num_orden__startswith=query)
        order_list = Orden.objects.filter(filter)
        print('filtro',filter)
        print('lista de ordenes',order_list)
    else:
        messages.error(request, 'Debe ingresar un numero de orden para buscar')
        return redirect('list_ordenes_admin')
    context = {
        'ordens' : order_list,
        'query' : query
    }
    print('contexto enviado', context)

    return render(request, 'gestion_pedidos/list_ordenes.html', context)

# def estado_search(request):
#     query = request.GET.get('searchEstado')
#     orden_status = OrdenStatus.choices

#     if query:
#         filter = Q(num_orden__startswith=query)
#         order_list = Orden.objects.filter(filter)
#         print('filtro',filter)
#         print('lista de ordenes',order_list)
#     else:
#         messages.error(request, 'Debe ingresar un numero de orden para buscar')
#         return redirect('list_ordenes_admin')
    
#     context = {
#         'ordens' : order_list,
#         'query' : query,
#         'statusorden' : orden_status
#     }
#     print('contexto enviado', context)

#     return render(request, 'gestion_pedidos/list_ordenes.html', context)
