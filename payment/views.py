from django.shortcuts import redirect,render
from django.views.decorators.csrf import csrf_exempt
import requests
import json
import random
from django.conf import settings
from cart.models import Cart
from orden.models import Orden, OrdenStatus
from django.contrib import messages
from orden.models import OrdenProducto
from django.utils.dateparse import parse_datetime



def crearTransaccion(request):
    user = request.user if request.user.is_authenticated else None
    cart = Cart.objects.filter(user=user).order_by('id').first()
    
    orden = Orden.objects.filter(user=user, status=OrdenStatus.CREATED).first()

    if not orden:
        try:
            orden = Orden.objects.create(user=user, cart=cart, status=OrdenStatus.CREATED)
        except Exception as e:
            orden = Orden.objects.create(user=user, cart=cart, status=OrdenStatus.CREATED)
            messages.error(request, f"Error al crear la orden: {str(e)}")
            return redirect('orden')

    if orden.delivery_method == 'PICKUP':
        orden.envio_total = 0  
    orden.update_total()  

    price = orden.total
    buy_order = orden.id
    session_id = str(random.randint(10000, 99999))
    amount = float(price)

    ruta = f"{settings.BASE_URL}/webpay/"

    payload = {
        "buy_order": buy_order,
        "session_id": session_id,
        "amount": amount,
        "return_url": ruta
    }

    payment_response  = pagarConWebpay(payload)

    if payment_response:
        token_ws = payment_response.get("token")
        url = payment_response.get("url")

        orden.token_ws = token_ws
        orden.save(update_fields=['token_ws'])

        return redirect(f"{url}?token_ws={token_ws}")
    else:
        messages.error(request, "Hubo un problema al procesar el pago. Intenta nuevamente.")
        return redirect('orden')


    
def pagarConWebpay(payload):
    endpoint = settings.WEBPAY_BASE_URL + "/rswebpaytransaction/api/webpay/v1.2/transactions"
    headers = {
        'Tbk-Api-Key-Id': settings.WEBPAY_COMMERCE_CODE,
        'Tbk-Api-Key-Secret': settings.WEBPAY_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.post(endpoint, json=payload, headers=headers)

    if response.status_code == 200:
        respuesta = json.loads(response.text)
        return {
            'token': respuesta.get('token'),
            'url': respuesta.get('url')
        } 
        
    else:
        print(f"Error al procesar el pago: {response.status_code} - {response.text}")
        return None

def obtener_estado_pago_webpay(token):
    url = settings.WEBPAY_BASE_URL + f"/rswebpaytransaction/api/webpay/v1.2/transactions/{token}"

    headers = {
        'Tbk-Api-Key-Id': settings.WEBPAY_COMMERCE_CODE,
        'Tbk-Api-Key-Secret': settings.WEBPAY_API_KEY,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.put(url, headers=headers) 
        return response.json()
    except Exception as e:
        print("Error al obtener estado:", e)
        return None

@csrf_exempt
def webpay_respuesta(request):
    token_ws = request.GET.get('token_ws') or request.POST.get('token_ws')

    print("Método de la solicitud:", request.method)
    print(f"Token recibido en return_url: {token_ws}")

    if not token_ws:
        return render(request, 'token_fallido.html', {'error':'token invalido'})
    
    print("Token recibido:", token_ws)

    resultado = obtener_estado_pago_webpay(token_ws)
    print("Resultado Webpay:", resultado)

    if resultado:
        estado = resultado.get('status')
        if estado == 'AUTHORIZED':
            if request.user.is_authenticated:
                orden = Orden.objects.filter(token_ws=token_ws).first()
                if orden:
                    total_original = orden.total
                    orden.status = OrdenStatus.PAYED
                    orden.save(update_fields=['status'])
                    print(f'estado actualizado: {Orden.status}')
                    cart = orden.cart
                    if cart:
                        for cart_product in orden.cart.cartproduct_set.all():
                            OrdenProducto.objects.create(
                                orden=orden,
                                producto=cart_product.productos,
                                quantity=cart_product.quantity
                            )
                        cart.productos.clear()
                        cart.update_totals()
                        print(f'carrito limpiado: {cart}')
                    orden.total = total_original
                    orden.save(update_fields=['total'])
                    transaction_date = resultado.get("transaction_date")
                    if transaction_date:
                        orden.fecha_pagada = parse_datetime(transaction_date)
                    orden.save(update_fields=['fecha_pagada'])
                    print(total_original)
            return render(request, 'confirmed.html', {'resultado': resultado})
        elif estado == 'INITIALIZED':
            return render(request, 'peding.html', {'resultado': resultado , 'token_ws': token_ws})
        elif estado == 'FAILED':
            return render(request, 'paymen_failed.html', {'resultado': resultado})
        else:
            return render(request, 'payment_unknown.html', {'resultado': resultado})
    else:
        return render(request, 'payment_failed.html', {'error': 'No se pudo obtener el estado del pago'})
    
