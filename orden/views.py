from django.shortcuts import get_object_or_404, render,redirect
from orden.utils import funcionOrden, breadcrumb
from cart.funciones import funcionCarrito
from django.contrib.auth.decorators import login_required
from profiles.models import Address
from profiles.forms import AddressForm,OrderAddressForm
from .models import DeliveryMethod, OrderAddress,Orden
from payment.views import crearTransaccion  
from django.contrib import messages
from orden.models import Orden, OrdenStatus
from django.db.models import Q


# Create your views here.
@login_required(login_url='login')
def orden(request):
    cart = funcionCarrito(request)
    orden = funcionOrden(cart, request)

    direccion_existente = Address.objects.filter(user=request.user).first()
    address_form = AddressForm(request.POST or None)
    
    if request.method == 'POST':
        if 'delivery_method' in request.POST:
            delivery_method = request.POST.get('delivery_method')
            if delivery_method == 'SHIPPING':
                orden.delivery_method = DeliveryMethod.SHIPPING
                orden.save() 
                orden.update_total()
            elif delivery_method == 'PICKUP':
                orden.delivery_method = DeliveryMethod.PICKUP
                orden.save()  
                orden.update_total()
        
        if 'pagar' in request.POST:
            return crearTransaccion(request)

        if not direccion_existente and orden.delivery_method == 'SHIPPING':
            address_form = AddressForm(request.POST)  
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()
                request.user.userprofile.address = address 
                request.user.userprofile.save()
                messages.success(request, "Dirección agregada al perfil con éxito.")
                return redirect('orden')
    
    breadcrumb_items = breadcrumb(products=True, confirmation=False)  

    return render(request, 'orden.html',{
        'cart': cart,
        'orden': orden,
        'direccion_existente': direccion_existente,
        'address_form': address_form,
        'breadcrumb' : breadcrumb_items,
    })

@login_required(login_url='login')
def modificar_direccion(request, orden_id):
    orden = Orden.objects.get(id=orden_id)
    direccion_existente = OrderAddress.objects.filter(order=orden).first()
    order_address_form = OrderAddressForm(request.POST or None)

    if request.method == 'POST':
        if order_address_form.is_valid():
            if direccion_existente:
                direccion_existente.calle = order_address_form.cleaned_data['calle']
                direccion_existente.num_direccion = order_address_form.cleaned_data['num_direccion']
                direccion_existente.comuna = order_address_form.cleaned_data['comuna']
                direccion_existente.ciudad = order_address_form.cleaned_data['ciudad']
                direccion_existente.save()
            else:
                address = order_address_form.save(commit=False)
                address.order = orden  
                address.user = request.user  
                address.save()

            return redirect('orden')  
        else:
            print("Form Errors:", order_address_form.errors)  

    return render(request, 'modificar_direccion.html', {
        'direccion_existente': direccion_existente,
        'address_form': order_address_form
    })

def add_new_address(request):
    if request.user.userprofile.address:
        address_form = AddressForm(instance=request.user.userprofile.address)
    else:
        address_form = AddressForm()

    if request.method == 'POST':
        address_form = AddressForm(request.POST, instance=request.user.userprofile.address)

        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.user = request.user
            address.save() 
            request.user.userprofile.address = address
            request.user.userprofile.save()
            messages.success(request, "Dirección agregada al perfil con éxito.")
            return redirect('orden') 

    return render(request, 'add_newaddress.html', {'address_form': address_form})
    
def historial_orden(request):
    user = request.user
    if user.is_authenticated:
        ordenes = Orden.objects.filter(user=request.user).order_by('-fecha_pagada').prefetch_related('productos_orden__producto')
        return render(request, 'historial_compra/historial_compras.html', {
            'ordenes': ordenes
        })
    else:
        messages.error(request, "Debes estar autenticado para ver tu historial de compras.")
        return redirect('login')

def detalle_compra(request, id):  
    orden = get_object_or_404(Orden, id=id) 
    return render(request, 'detalle_compra.html', {
        'orden': orden
    })


def cancelar_orden(request,id):
    orden = get_object_or_404(Orden, id=id)
    try:
        orden.status = OrdenStatus.CANCELED
        orden.save(update_fields=['status'])
    except:
        messages.error(request, 'No se logro cancelar la orden')

    return redirect('historial_orden')


def compra_search(request):
    query = request.GET.get('searchcompraQ')
    if query:
        filter = Q(num_orden__startswith=query)
        print(filter)
        orden_list = Orden.objects.filter(filter)
        print('true',orden_list)
    else:
        orden_list = Orden.objects.filter(user=request.user).order_by('-fecha_pagada').prefetch_related('productos_orden__producto')
        print('false',orden_list)
    context = {
        'ordenes' : orden_list,
        'query' : query
    }

    return render(request, 'historial_compra/historial_compras.html', context)



