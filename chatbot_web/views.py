from django.shortcuts import render
from django.http import JsonResponse
from .utils_bot import consulta_stock, consultar_estado_pedido

MAIN_MENU_OPTIONS = [
    "1- Consulta de Productos",
    "2- Estado de pedido",
    "3- Información general",
    "4- Contactar con personal"
]

OPCION_PRODUCTOS_MENU = [
    "1- Stock de producto",
    "2- Producto destacado",
    "3- Volver al menú principal"
]

OPCION_INFOGENERAL_MENU = [
    "1- Guia de compra",
    "2- Contacto y ubicacion",
    "3- Volver al menú principal"
]

# Funcion para devolver menu principal apenas inicia el chat
def menu_principal_start():
    return JsonResponse({
        'mensaje': "Bienvenido!.<br>Elige una opción:",
        'opciones': MAIN_MENU_OPTIONS,
        'estado': 'menu'
    })

# Función para devolver el menú principal
def menu_principal_response():
    return JsonResponse({
        'mensaje': "Elige una opción:",
        'opciones': MAIN_MENU_OPTIONS,
        'estado': 'menu'
    })

# Función para devolver menu de opcion 1.Consulta de Productos
def menu_productos():
    return JsonResponse({
        'mensaje': "Estas en Productos<br><br>Elige una opción:",
        'opciones': OPCION_PRODUCTOS_MENU,
        'estado': 'productos'
    })

def menu_informacion_general():
    return JsonResponse({
        'mensaje': "Estas en Informacion general<br><br>Elige una opción:",
        'opciones': OPCION_INFOGENERAL_MENU,
        'estado': 'info_general'
    })


def menu_bot_view(request):
    estado = request.GET.get('estado', 'menu')
    user_input = request.GET.get('chatbot-input', '').strip()

    # Estado inicial: Menú principal
    if estado == 'menu':
        if not user_input:  # Primera vez que se abre el chatbot
            return menu_principal_start()

        # El usuario eligió una opción del menú principal
        if user_input == '1':
            return menu_productos()
        elif user_input == '2':
            return JsonResponse({
                'mensaje': "Has seleccionado: Estado de pedido<br><br>Por favor, ingrese todos los dígitos del número de pedido.",
                'opciones': [
                    "1- Volver al menú principal"
                ],
                'estado': 'buscar_pedido_m'
            })
        elif user_input == '3':
            return menu_informacion_general()
        elif user_input == '4':
            return JsonResponse({
                'mensaje': "Has seleccionado: Contactar con personal<br>",
                'opciones': [ 
                    "Si desea comunicarse con personal ir via WhatsApp +569 12341234 ",
                    "1- Volver al menú principal"
                ],
                'estado': 'contactar_personal'
            })
        else:
            return JsonResponse({
                'mensaje': "Opción no válida. Por favor elige 1, 2, 3 o 4.",
                'opciones': MAIN_MENU_OPTIONS,
                'estado': 'menu'
            })

    # Estado: Sección de Productos
    elif estado == 'productos':
        if user_input == '1':
            return JsonResponse({
                'mensaje': "Has seleccionado: Consultar stock de producto<br><br>Para consultar stock, escribe el SKU o código del producto.",
                'opciones': [
                    "1- Volver a productos",
                    "2- Volver al menú principal"
                ],
                'estado': 'consultar_stock'
            })
        elif user_input == '2':
            return JsonResponse({
                'mensaje': "Has seleccionado: Producto destacado<br><br>Producto destacado del mes: <br><b>Smartphone XYZ</b><br>Precio: $299.99<br>Stock disponible: 15 unidades",
                'opciones': [
                    "1- Volver a productos",
                    "2- Volver al menú principal"
                ],
                'estado': 'producto_destacado'
            })
        elif user_input == '3':
            return menu_principal_response() 
        else:
            return JsonResponse({
                'mensaje': "Opción no válida. Por favor elige una opción válida.",
                'opciones': OPCION_PRODUCTOS_MENU,
                'estado': 'productos'
            })

    # Estado: Consulta de estado pedido
    elif estado == 'buscar_pedido_m':
        if user_input == '1':
            return menu_principal_response()
        else:
            resultado = consultar_estado_pedido(user_input)
            return JsonResponse({
                'mensaje': f"{resultado}",
                'opciones': [
                    "Escribe otro número de pedido para consultar<br>",
                    "1- Volver al menú principal"
                ],
                'estado': 'buscar_pedido_m'
            })
            
    # Estado: Información General
    elif estado == 'info_general':
        if user_input == '1':
            return JsonResponse({
                'mensaje': "Has seleccionado: Guia de compra",
                'opciones': [ "Instrucciones de cómo comprar con link de página <br>",
                    "1- Volver a información general",
                    "2- Volver al menú principal"
                ],
                'estado': 'guia_compra'
            })
        elif user_input == '2':
            return JsonResponse({
                'mensaje': "Has seleccionado: Contacto y ubicación",
                'opciones': [ "Información con link de contacto y ubicación <br>",
                    "1- Volver a información general",
                    "2- Volver al menú principal"
                ],
                'estado': 'contacto_ubicacion'
            })
        elif user_input == '3':
            return menu_principal_response() 
        else:
            return JsonResponse({
                'mensaje': "Opción no válida. Por favor elige una opción válida.",
                'opciones': OPCION_INFOGENERAL_MENU,
                'estado': 'info_general'
            })
        
    elif estado == 'guia_compra':
        if user_input == '1':
            return menu_informacion_general()
        elif user_input == '2':
            return menu_principal_response()
        else:
            return JsonResponse({
                'mensaje': "Opción no válida. Por favor elige una opción válida.",
                'opciones': [
                    "1- Volver a información general",
                    "2- Volver al menú principal"
                ],
                'estado': 'guia_compra'
            })

    elif estado == 'contacto_ubicacion':
        if user_input == '1':
            return menu_informacion_general()
        elif user_input == '2':
            return menu_principal_response()
        else:
            return JsonResponse({
                'mensaje': "Opción no válida. Por favor elige una opción válida.",
                'opciones': [
                    "1- Volver a productos",
                    "2- Volver al menú principal"
                ],
                'estado': 'productos'
            })

    # Estado: Consultar Stock
    elif estado == 'consultar_stock':
        if user_input == '1':
            return menu_productos()
        elif user_input == '2':
            return menu_principal_response()
        else:
            resultado = consulta_stock(user_input)
            return JsonResponse({
                'mensaje': f"Stock disponible:<br> {resultado}",
                'opciones': [
                    "Escribe otro SKU para consultar",
                    "1- Volver a productos",
                    "2- Volver al menú principal"
                ],
                'estado': 'consultar_stock'
            })

    # Estado: Producto Destacado
    elif estado == 'producto_destacado':
        if user_input == '1':
            return menu_productos()
        elif user_input == '2':
            return menu_principal_response()

    elif estado == 'contactar_personal':
        if user_input == '1':
            return menu_principal_response() 
        else:
            return JsonResponse({
                'mensaje': "Opción no válida. Por favor elige una opción válida.",
                'opciones': [ 
                    "Si desea comunicarse con personal ir via WhatsApp +569 12341234 <br>",
                    "1- Volver al menú principal"
                ],
                'estado': 'contactar_personal'
            })
        
    # Estado por defecto: volver al menú
    return menu_principal_response() 


def inicio_bot(request):
    return render(request, 'chatbot.html')