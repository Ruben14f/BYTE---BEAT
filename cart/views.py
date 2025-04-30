from django.shortcuts import render
from .funciones import *
from products.models import Product
from .models import CartProduct
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from orden.utils import breadcrumb

# Create your views here.

def cart(request):
    cart = funcionCarrito(request)
    
    print(cart.productos.all())

    breadcrumb_items = breadcrumb(Cart=True, products=False, confirmation=False)  

    return render(request, 'cart_detail.html', {
        'cart': cart,
        'breadcrumb' : breadcrumb_items
    })


def addCart(request):
    cart = funcionCarrito(request)
    product = get_object_or_404(Product, pk=request.POST.get('product_id'))
    quantity = int(request.POST.get('quantity', 1))
    
    product_cart = CartProduct.objects.crearActualizar(cart=cart, productos=product, quantity=quantity)

    messages.info(request, 'Producto agregado al carrito correctamente')
    return render(request, 'cart_detail.html',{
        'product': product,
        'cart': cart
    })

def remove(request):
    cart = funcionCarrito(request)
    product = get_object_or_404(Product, pk=request.POST.get('product_id'))

    cart.productos.remove(product)
    
    messages.info(request, 'Producto eliminado de carrito')
    return redirect('cart')

def update_cart_product(request):
    if request.method == 'POST':
        cart_product_id = request.POST.get('cart_product_id')
        new_quantity = int(request.POST.get('new_quantity'))

        try:
            cart_product = CartProduct.objects.get(id=cart_product_id)
            cart_product.update_quantity(new_quantity)
            cart_product.cart.update_totals()
            return redirect('cart')

        except CartProduct.DoesNotExist:
            messages.error(request, "El producto no se encuentra en el carrito")
            return redirect('cart')

    return redirect('cart') 
