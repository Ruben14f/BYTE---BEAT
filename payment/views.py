from django.shortcuts import redirect,render
from django.urls import reverse
import requests
import json
import random
from django.conf import settings
from cart.models import Cart
from orden.models import Orden, OrdenStatus
from django.contrib import messages
from orden.models import OrdenProducto
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from django.core.mail import send_mail
import os
from django.template.loader import render_to_string
from django.db import transaction
from profiles.models import UserProfile





def crearTransaccion(request):
    user = request.user if request.user.is_authenticated else None
    cart = Cart.objects.filter(user=user).order_by('-id').first()
    orden = Orden.objects.filter(user=user, status=OrdenStatus.CREATED, token_ws__isnull=True).order_by('-ordenID').first()

    if not user:
        messages.error(request, "Debes iniciar sesión para continuar con el pago.")
        return redirect('login')
    
    nombre = user.first_name.strip() if user.first_name else ''
    apellido = user.last_name.strip() if user.last_name else ''
    try:
        perfil = user.userprofile
        telefono = perfil.phone_number.strip() if perfil.phone_number else ''
        if perfil.address:
            direccion = perfil.address.full_address()  # Asegúrate que full_address() esté bien implementado
        else:
            direccion = ''
    except UserProfile.DoesNotExist:
        direccion = ''
        telefono = ''
    print(f"nombre: '{nombre}', apellido: '{apellido}', direccion: '{direccion}', telefono: '{telefono}'")
    print(user.userprofile  )
    profile = getattr(user, 'profile', None)
    if profile:
        print(f"direccion DB: '{profile.direccion}'")
        print(f"telefono DB: '{profile.telefono}'")
    else:
        print("No se encontró perfil asociado")
    if not all([nombre, apellido, direccion, telefono]):
        messages.error(request, "Debes completar nombre, apellido, dirección y teléfono antes de continuar.")
        return redirect('edit_profile')
    
    if not orden:
        try:
            orden = Orden.objects.create(user=user, cart=cart, status=OrdenStatus.CREATED)
        except Exception as e:
            messages.error(request, f"Error al crear la orden: {str(e)}")
            return redirect('orden')


    price = orden.total
    buy_order = orden.id
    session_id = str(random.randint(10000, 99999))
    amount = float(price)

    ruta = request.build_absolute_uri(reverse('webpay_respuesta'))

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
                orden = Orden.objects.filter(token_ws=token_ws, status=OrdenStatus.CREATED).first()
                
                if orden:
                    if orden.status == OrdenStatus.PAYED:
                        return render(request, 'confirmed.html', {'resultado': resultado})
                    
                    orden.status = OrdenStatus.PAYED
                    orden.save(update_fields=['status'])
                    print(f'estado actualizado: {Orden.status}')
                    original_total = orden.total

                    cart = orden.cart

                    if cart:
                        try:
                            with transaction.atomic():
                                for cart_product in orden.cart.cartproduct_set.all():
                                    product = cart_product.productos
                                    quantity = cart_product.quantity

                                    if product.stock >= cart_product.quantity:
                                        product.stock -= quantity
                                        product.save()

                                        OrdenProducto.objects.create(
                                        orden=orden,
                                        producto=cart_product.productos,
                                        quantity=cart_product.quantity)
                                    else:
                                        messages.error(request, f"Stock insuficiente para el producto {product.name}.")
                                        return redirect('orden')    
                                cart.productos.clear()
                                cart.update_totals()
                                print(f'carrito limpiado: {cart}')
                        except Exception as e:
                            messages.error(request, f"Error al procesar la transacción")
                            return redirect('orden')

                    transaction_date = resultado.get("transaction_date")
                    print("transaction_date cruda:", transaction_date)

                    if transaction_date:
                        parsed_date = parse_datetime(transaction_date)
                        print("parsed_date:", parsed_date)
                        if parsed_date:
                            orden.fecha_pagada = timezone.localtime(parsed_date)
                            print("Fecha con hora local guardada:", orden.fecha_pagada)

                    orden.total = original_total
                    orden.save(update_fields=['total','fecha_pagada'])
                    print(f"Total después de la transacción: {orden.total}")

                    #envio de correo de confirmacion del pedido
                    confirmacion_pedido_email(request, token_ws)

            return render(request, 'confirmed.html', {'resultado': resultado})
        elif estado == 'INITIALIZED':
            return render(request, 'peding.html', {'resultado': resultado , 'token_ws': token_ws})
        elif estado == 'FAILED':
            return render(request, 'paymen_failed.html', {'resultado': resultado})
        else:
            return render(request, 'payment_unknown.html', {'resultado': resultado})
    else:
        return render(request, 'paymen_failed.html', {'error': 'No se pudo obtener el estado del pago'})
    


def confirmacion_pedido_email(request,token_ws):
    orden = Orden.objects.filter(token_ws=token_ws, status=OrdenStatus.PAYED).first()

    print('orden pagada y enviando correo',orden)
    email = request.user.email if request.user.is_authenticated else None
    print(email)
    email_host = os.environ.get('EMAIL_HOST_USER')
    print(email_host)

    html_message = render_to_string('email_confirm.html', {
        'orden' : orden
    })
    print("HTML generado para el correo:\n", html_message)
    
    send_mail(
        'Pedido confirmado',
        'Detalle del pedido confirmado:',
        from_email=email_host, 
        recipient_list = [email],
        fail_silently=False,
        html_message= html_message
    )

    print('correo enviado',send_mail)

    messages.success(request, 'compra confirmada y correo enviado')
