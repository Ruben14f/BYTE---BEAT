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
    orden_status = OrdenStatus.choices
    print('estados disponibles vista ordenes', orden_status)
    return render(request, 'gestion_pedidos/list_ordenes.html',{
        'ordens' : ordenes,
        'statusorden' : orden_status
    })

def orden_search(request):
    query = request.GET.get('searchNumOrden')
    orden_status = OrdenStatus.choices
    if query:
        filter = Q(num_orden__startswith=query)
        order_list = Orden.objects.filter(filter).order_by('-fecha_pagada')
        print('filtro',filter)
        print('lista de ordenes',order_list)
    else:
        messages.error(request, 'Debe ingresar un numero de orden para buscar')
        return redirect('list_ordenes_admin')
    context = {
        'ordens' : order_list,
        'querynumorden' : query,
        'statusorden' : orden_status
    }
    print('contexto enviado', context)

    return render(request, 'gestion_pedidos/list_ordenes.html', context)

def estado_search(request):
    query = request.GET.get('searchEstado')
    orden_status = OrdenStatus.choices
    print('estados disponibles vista filtro', orden_status)

    label_to_value = {
        label.lower() : value 
        for value, label in orden_status}
    print('Query buscada',query)
    print('estados disponibles vista filtro mapeado', orden_status)
    if query: 
        internal_value = label_to_value.get(query.lower())
        if internal_value:
            filter = Q(status__startswith=internal_value)
            order_list = Orden.objects.filter(filter).order_by('-fecha_pagada')
            print('filtro',filter)
            print('lista de ordenes',order_list)
        elif query.lower() == 'borrarfiltro':
            messages.success(request, 'Filtro eliminar')
            return redirect('list_ordenes_admin')
    else:
        print('Query buscada',query)
        messages.error(request, 'Debe seleccionar un numero de estado para filtrar')
        return redirect('list_ordenes_admin')
    
    context = {
        'ordens' : order_list,
        'queryestado' : query,
        'statusorden' : orden_status
    }
    print('contexto enviado', context)

    return render(request, 'gestion_pedidos/list_ordenes.html', context)
