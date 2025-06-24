from django.shortcuts import render, get_object_or_404, redirect
from .forms import ProductForm
from .utils import *
from django.contrib import messages
from products.models import Product, Brand, Category,ProductStatus
from orden.models import Orden, OrdenStatus
from profiles.models import UserProfile
from django.db.models import Q, Count,F, Sum
from users.models import User
from django.core.mail import send_mail
import os
from django.template.loader import render_to_string
from django.utils.timezone import now, localtime
from django.utils import formats
from django.core.paginator import Paginator

#GESTION DE PRODUCTOS
def listado_productos(request):
    productos = Product.objects.all()
    marca = Brand.objects.all()
    categorias = Category.objects.all()
    product_status = ProductStatus.choices

    paginator = Paginator(productos, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    resumen_estados_qs = (
        productos
        .values('status')
        .annotate(total=Count('id'))
    )

    resumen_estadosp = {
        dict(ProductStatus.choices)[item['status']]: item['total']
        for item in resumen_estados_qs
    }

    #Total de productos
    t_productos = total_productos()

    #Total productos activos
    t_productos_activos = total_productos_activos()

    #Total de productos con stock bajo
    t_stock_bajo = productos_stock_bajo()

    #Total de productos sin stock
    t_sin_stock = productos_sin_stock()

    hora_actual = localtime(now()).date() 
    dia_de_la_semana = formats.date_format(hora_actual, "l")


    return render(request, 'gestion_productos/list_product.html',{
        'products': page_obj,
        'brands' : marca,
        'categories' : categorias,
        'statusproduct' : product_status,
        'resumen_estadosp' : resumen_estadosp,
        'total_productos' : t_productos,
        'total_productos_activos' : t_productos_activos,  
        'total_stock_bajo' : t_stock_bajo,
        'total_sin_stock' : t_sin_stock,
        'fecha_formateada': hora_actual,
        'dia_de_la_semana': dia_de_la_semana,
    })
    
def agregar_producto(request):
    form = ProductForm()

    if request.method == 'POST':
        formulario = ProductForm(data=request.POST, files=request.FILES)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, 'Producto creado correctamente')
            return redirect('list_product_admin')
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
            if formulario.has_changed():  
                formulario.save()
                messages.success(request, 'Producto editado correctamente')
                return redirect('list_product_admin')
            else:
                messages.info(request, 'No se han realizado cambios en el producto.')
                return redirect('editar_product_admin', id=id) 

    return render(request, 'gestion_productos/editar_product.html', {
        'productForm': form,
        'producto': producto
    })

def eliminar_producto(request, id):
    producto = get_object_or_404(Product, id=id)
    producto.delete()
    return redirect('list_product_admin')

def detail_product(request, id):
    product = get_object_or_404(Product, id=id)
    
    return render(request, 'gestion_productos/detail_product.html', {
        'product' : product
    })

#Filtros productos
def sku_search(request):
    query = request.GET.get('searchSku')
    if query:
        filter = Q(sku__startswith=query)
        product_list = Product.objects.filter(filter)
        if not product_list:
            messages.error(request, 'No se encontraron productos con ese sku')
            return redirect('list_product_admin')
        print('filtro',filter)
        print('lista de productos',product_list)
    else:
        messages.error(request, 'Debe ingresar un sku valido')
        return redirect('list_product_admin')
    
    context ={
        'products' : product_list,
        'queryOrden' : query
    }
    return render(request, 'gestion_productos/list_product.html', context)

def marca_search(request):
    query = request.GET.get('searchMarca')
    marca = Brand.objects.all()
    if query and query != 'borrarFiltro':
        filter = Q(brand__name__icontains=query)
        product_list = Product.objects.filter(filter)
        print('filtro',filter)
        print('lista de marcas',product_list)
    elif query == 'borrarFiltro':
        messages.success(request, 'Filtro eliminado')
        return redirect('list_product_admin') 
    else:
        messages.error(request, 'Debe ingresar una marca valida')
        return redirect('list_product_admin')
    
    context ={
        'brands' : marca,
        'products' : product_list,
        'queryMarca' : query
    }
    return render(request, 'gestion_productos/list_product.html', context)

def categoria_search(request):
    query =request.GET.get('searchCategoria')
    categoria = Category.objects.all()
    if query and query != 'borrarFiltro':
        filter = Q(category__name__icontains=query)
        product_list = Product.objects.filter(filter)
        print('filtro',filter)
        print('lista de categorias',product_list)
    elif query == 'borrarFiltro':
        messages.success(request, 'Filtro eliminado')
        return redirect('list_product_admin') 
    else:
        messages.error(request, 'Debe ingresar una categoria valida')
        return redirect('list_product_admin')
    context = {
        'categories' : categoria,
        'products' : product_list,
        'queryCategory' : query
    }
    return render(request, 'gestion_productos/list_product.html', context)

def estado_product_search(request):
    query = request.GET.get('searchEstadoProducto')
    product_status = ProductStatus.choices
    print('estados disponibles vista filtro productostatus', product_status)
    
    label_to_value = {
        label.lower() : value 
        for value, label in product_status}
    print('Query buscada',query)
    print('estados disponibles vista filtro mapeado productostatus', product_status)
    if query: 
        internal_value = label_to_value.get(query.lower())
        if internal_value:
            filter = Q(status__startswith=internal_value)
            product_list = Product.objects.filter(filter).order_by('-created_at')
            print('filtro productostatus',filter)
            print('lista de products productostatus',product_list)
        elif query.lower() == 'borrarfiltro':
            messages.success(request, 'Filtro eliminado')
            return redirect('list_product_admin')
    else:
        print('Query buscada',query)
        messages.error(request, 'Debe seleccionar un estado del producto para filtrar')
        return redirect('list_product_admin')
    
    context = {
        'products' : product_list,
        'queryestadoproducto' : query,
        'statusproduct' : product_status
    }
    print('contexto enviado', context)

    return render(request, 'gestion_productos/list_product.html', context)
    

#GESTION DE PEDIDOS
def listado_ordenes(request):
    ordenes = Orden.objects.exclude(status='CREATED').order_by('-fecha_pagada')
    orden_status = OrdenStatus.choices

    paginator = Paginator(ordenes, 10) 
    page_number = request.GET.get('page',1)
    page_obj = paginator.get_page(page_number)
    
    resumen_estados_qs = (
        ordenes
        .values('status')
        .annotate(total=Count('id'))
    )

    # Convertir a dict con los nombres legibles
    resumen_estados = {
        dict(OrdenStatus.choices)[item['status']]: item['total']
        for item in resumen_estados_qs
    }
    
    #Total de pedidos
    total_ordenes_hoy = total_pedidos_hoy()

    #Total de ordenes completadas
    total_completadas = total_pedidos_completados()

    #Total ingresos por ordenes
    total_ingresos = ingresos_totales()

    hora_actual = localtime(now()).date() 
    dia_de_la_semana = formats.date_format(hora_actual, "l")


    return render(request, 'gestion_pedidos/list_ordenes.html',{
        'ordens' : page_obj,
        'statusorden' : orden_status,
        'resumen_estados' : resumen_estados,
        'total_ordenes' : total_ordenes_hoy,
        'total_completadas' : total_completadas,
        'total_ingresos' : total_ingresos,
        'fecha_formateada': hora_actual,
        'dia_de_la_semana': dia_de_la_semana,
    })

def detail_orden(request, id):
    orden = get_object_or_404(Orden, id=id)
    user = orden.user

    subtotal = orden.productos_orden.aggregate(
        total=Sum(F('quantity') * F('producto__price'))
    )['total'] or 0

    try:
        profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        profile = None 

    context = {
        'orden': orden,
        'user': user,
        'profiledatos': profile,
        'subtotal': subtotal,
    }
    return render(request, 'gestion_pedidos/detail_orden.html', context)

def update_status_orden(request, id):
    orden = get_object_or_404(Orden, id=id)
    orden_status = OrdenStatus.choices
    user = User.objects.get(id=orden.user.id)
    usermail = user.email
    
    label_to_value = {
        label.lower() : value 
        for value, label in orden_status}
    
    print('estados de ordenes vista update', orden_status)
    print('orden', orden.id,orden.get_status_display)
    print('orden', orden.id,orden.status)
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estadoOrdenUpdate')
        internal_value = label_to_value.get(nuevo_estado.lower())
        print('nuevo estado', nuevo_estado)
        print('nuevo estado internal_value', orden_status)
        if not orden_status:
            messages.success(request, 'Estado invalido')
        if internal_value == orden.status:
            messages.error(request, 'La orden ya se encuentra en ese estado.')
        else:
            orden.status = internal_value
            orden.save()
            messages.success(request, 'Estado de la orden actualizado correctamente')
            send_email(request, nuevo_estado, usermail, orden, user)
            print('testmail',send_mail)
    return redirect('list_ordenes_admin')

def send_email(request, nuevo_estado, usermail, orden, user):
    print('nuevo estado email', nuevo_estado)
    print('email user change status',usermail)
    email_host = os.environ.get('EMAIL_HOST_USER')
    
    html_message = render_to_string('gestion_productos/email_update_status.html', {
        'orden' : orden,
        'user' : user
    })
    
    send_mail(
        'Actualizacion de estado de orden',
        'Detalle del pedido:',
        from_email=email_host, 
        recipient_list = [usermail],
        fail_silently=False,
        html_message= html_message
    )
    
    print('correo enviado desde', email_host ,'hacia' , usermail, orden.id)

#Filtros ordenes
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
            messages.success(request, 'Filtro eliminado')
            return redirect('list_ordenes_admin')
    else:
        print('Query buscada',query)
        messages.error(request, 'Debe seleccionar un estado para filtrar')
        return redirect('list_ordenes_admin')
    
    context = {
        'ordens' : order_list,
        'queryestado' : query,
        'statusorden' : orden_status
    }
    print('contexto enviado', context)

    return render(request, 'gestion_pedidos/list_ordenes.html', context)
