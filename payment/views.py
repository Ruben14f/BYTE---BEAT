from django.shortcuts import redirect,render
import requests
import json
import random
from django.conf import settings
from cart.models import Cart
from orden.models import Orden, OrdenStatus
from django.contrib import messages



def crearTransaccion(request):
    user = request.user if request.user.is_authenticated else None
    orden = Orden.objects.filter(user=user, status=OrdenStatus.CREATED).first()

    if not orden:
        # Si no existe una orden activa, crear una nueva
        cart = Cart.objects.filter(user=user).order_by('id').first()
        try:
            orden = Orden.objects.create(user=user, cart=cart, status=OrdenStatus.CREATED)
        except Exception as e:
            orden = Orden.objects.create(user=user, cart=cart, status=OrdenStatus.CREATED)
            messages.error(request, f"Error al crear la orden: {str(e)}")
            return redirect('carrito')

    # Asegurarse de que el costo de envío esté actualizado
    if orden.delivery_method == 'PICKUP':
        orden.envio_total = 0  # Asegúrate de que no haya costo de envío
    orden.update_total()  # Actualiza el total de la orden

    price = orden.total
    buy_order = orden.id
    session_id = str(random.randint(10000, 99999))
    amount = float(price)

    ruta = f"{settings.BASE_URL}/carro/webpay-respuesta"

    payload = {
        "buy_order": buy_order,
        "session_id": session_id,
        "amount": amount,
        "return_url": ruta
    }

    payment_url = pagarConWebpay(payload)

    if payment_url:
        return redirect(payment_url)
    else:
        messages.error(request, "Hubo un problema al procesar el pago. Intenta nuevamente.")
        return redirect('carrito')


    
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
        token_ws = respuesta.get('token') 
        payment_url = respuesta.get('url')  
        
        if payment_url:
            return f"{payment_url}?token_ws={token_ws}"
    else:
        print(f"Error al procesar el pago: {response.status_code} - {response.text}")
        return None

def obtener_estado_pago_webpay(token):
    url = settings.WEBPAY_BASE_URL + f"/webpay/plus/v1.0/transactions/{token}"

    headers = {
        'Tbk-Api-Key-Id': settings.WEBPAY_COMMERCE_CODE,
        'Tbk-Api-Key-Secret': settings.WEBPAY_API_KEY,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return None
