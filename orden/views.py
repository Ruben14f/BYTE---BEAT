from django.shortcuts import render,redirect
from orden.utils import funcionOrden, breadcrumb
from cart.funciones import funcionCarrito
from django.contrib.auth.decorators import login_required
from profiles.models import Address
from profiles.forms import AddressForm,OrderAddressForm
from .models import OrderAddress,Orden


# Create your views here.
@login_required(login_url='login')
def orden(request):
    cart = funcionCarrito(request)
    orden = funcionOrden(cart, request)

    direccion_existente = Address.objects.filter(user=request.user).first()
    address_form = AddressForm(request.POST or None)

    if request.method == 'POST':
        # delivery_method  = request.POST.get('delivery_method')
        # if delivery_method == 'PICKUP':
        #     orden.delivery_method = DeliveryMethod.PICKUP
        #     orden.save()
        # elif delivery_method == 'SHIPPING':
        #     orden.delivery_method = DeliveryMethod.SHIPPING
        #     orden.save()

        if not direccion_existente:  # Solo se guarda la dirección si no existe una
            address_form = AddressForm(request.POST)  # Asegúrate de instanciar con POST
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user 
                address.save()
                request.user.userprofile.address = address
                request.user.userprofile.save()

                return redirect('orden')
    
    breadcrumb_items = breadcrumb(Cart=False, products=True, confirmation=False)  

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


# @login_required(login_url='login')
# def confirmacion(request):
#     cart = funcionCarrito(request)
#     orden = funcionOrden(cart, request)

