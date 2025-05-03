from django.http import HttpResponseServerError
from django.shortcuts import render
from .funciones import *
from products.models import Product
from .models import CartProduct
from django.contrib import messages
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
import traceback



# Create your views here.

def cart(request):
    cart = funcionCarrito(request)
    
    print(cart.productos.all())


    return render(request, 'cart_detail.html', {
        'cart': cart,
    })


def addCart(request):
    try:
        cart = funcionCarrito(request)
        product = get_object_or_404(Product, pk=request.POST.get('product_id'))
        quantity = int(request.POST.get('quantity', 1))

        product_cart = CartProduct.objects.crearActualizar(cart=cart, productos=product, quantity=quantity)

        messages.info(request, 'Producto agregado al carrito correctamente')
        
    except Exception as e:
        messages.error(request, f'Ocurrió un error al agregar el producto: {str(e)}')
        error_trace = traceback.format_exc()
        print("🔥 ERROR DETECTADO EN addCart:\n", error_trace)
        return HttpResponseServerError(f"<pre>{error_trace}</pre>")

    return render(request, 'cart_detail.html', {
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
