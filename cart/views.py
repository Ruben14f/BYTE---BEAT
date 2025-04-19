from django.shortcuts import render
from .funciones import *
from products.models import Product
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404

# Create your views here.

def cart(request):
    cart = funcionCarrito(request)
    
    print(cart.productos.all())

    return render(request, 'cart_detail.html', 
        {'cart': cart
    })


def addCart(request):
    cart = funcionCarrito(request)
    product = get_object_or_404(Product, pk=request.POST.get('product_id'))

    cart.productos.add(product)
    messages.success(request, 'Producto agregado al carrito')

    return render(request, 'add_to_cart.html',{
        'product': product,
    })

def remove(request):
    cart = funcionCarrito(request)
    product = get_object_or_404(Product, pk=request.POST.get('product_id'))

    cart.productos.remove(product)
    messages.info(request, 'Producto eliminado de carrito')
    return redirect('cart')