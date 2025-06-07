from django.shortcuts import render
from django.http import JsonResponse
from .utils_bot import consulta_stock, consultar_estado_pedido

MAIN_MENU_OPTIONS = [
    "1- Consulta de Productos",
    "2- Estado del pedido",
    "3- Información general",
    "4- Contactar con personal"
]

# Función para devolver la respuesta del menú principal
def menu_principal_response():
    return JsonResponse({
        'mensaje': "Bienvenido!.<br>Elige una opción:",
        'opciones': MAIN_MENU_OPTIONS,
        'estado': 'menu'
    })

def menu_bot_view(request):
    estado = request.GET.get('estado', 'menu')
    user_input = request.GET.get('chatbot-input', '').strip()

    # Estado inicial: Menú principal
    if estado == 'menu':
        if not user_input:  # Primera vez que se abre el chatbot
            return menu_principal_response()

        # El usuario eligió una opción del menú principal
        if user_input == '1':
            return JsonResponse({
                'mensaje': "Has seleccionado: Productos<br><br>Elige una opción:",
                'opciones': [
                    "1- Consultar stock de producto",
                    "2- Producto destacado",
                    "3- Volver al menú principal"
                ],
                'estado': 'productos'
            })
        elif user_input == '2':
            return JsonResponse({
                'mensaje': "Has seleccionado: Estado de pedido<br><br>Por favor, ingrese todos los digitos del número de pedido.",
                'opciones': [
                    "Ejemplo: Escribe '001' para buscar pedido #001",
                    "Escribe 'volver' para regresar"
                ],
                'estado': 'buscar_pedido'
            })
        else:
            return JsonResponse({
                'mensaje': "Opción no válida. Por favor elige 1, 2 ,3 4 .",
                'opciones': MAIN_MENU_OPTIONS,
                'estado': 'menu'
            })

    # Estado: Sección de Productos
    elif estado == 'productos':
        if user_input == '1':
            return JsonResponse({
                'mensaje': "Has seleccionado: Consultar stock de producto<br><br>Para consultar stock, escribe el SKU o código del producto.",
                'opciones': [
                    "Escribe 'volver' para regresar"
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
        elif user_input == '2':
            return menu_principal_response()  # Volver al menú principal
        else:
            return JsonResponse({
                'mensaje': "Opción no válida. Por favor elige una opción válida.",
                'opciones': [
                    "1- Consultar stock de producto",
                    "2- Producto destacado",
                    "3- Volver al menú principal"
                ],
                'estado': 'productos'
            })

    # Estado: Consulta de estado pedido
    elif estado == 'buscar_pedido':
        if user_input.lower() == 'volver':
            return menu_principal_response()  # Volver al menú principal
        else:
            resultado = consultar_estado_pedido(user_input)
            return JsonResponse({
                'mensaje': f"{resultado}",
                'opciones': [
                    "Escribe otro numero de pedido para consultar",
                    "Escribe 'volver' para regresar al menu principal"
                ],
                'estado': 'pedidos'
            })


    # Estado: Consultar Stock
    elif estado == 'consultar_stock':
        if user_input.lower() == 'volver':
            return JsonResponse({
                'mensaje': "Has seleccionado: Volver<br><br>Elige una opción:",
                'opciones': [
                    "1- Consultar stock de producto",
                    "2- Producto destacado",
                    "3- Volver al menú principal"
                ],
                'estado': 'productos'
            })
        else:
            resultado = consulta_stock(user_input)
            return JsonResponse({
                'mensaje': f"Stock disponible:<br> {resultado}",
                'opciones': [
                    "Escribe otro SKU para consultar",
                    "Escribe 'volver' para regresar a productos"
                ],
                'estado': 'consultar_stock'
            })

    # Estado: Producto Destacado
    elif estado == 'producto_destacado':
        if user_input == '1':
            return JsonResponse({
                'mensaje': "Más productos destacados:<br>- Laptop Pro: $899.99<br>- Auriculares Premium: $199.99<br>- Tablet Ultra: $449.99",
                'opciones': [
                    "1- Volver a productos",
                    "2- Volver al menú principal"
                ],
                'estado': 'productos_extra'
            })
        elif user_input == '2':
            return JsonResponse({
                'mensaje': "Has seleccionado Productos.<br>Elige una opción:",
                'opciones': [
                    "1- Consultar stock de producto",
                    "2- Producto destacado",
                    "3- Volver al menú principal"
                ],
                'estado': 'productos'
            })
        elif user_input == '3':
            return menu_principal_response()  # Volver al menú principal

    # Estados adicionales para manejo de navegación
    elif estado == 'ver_pedidos':
        if user_input == '2':
            return JsonResponse({
                'mensaje': "Has seleccionado Pedidos.<br>Elige una opción:",
                'opciones': [
                    "1- Ver pedidos pendientes",
                    "2- Crear nuevo pedido",
                    "3- Buscar pedido por ID",
                    "4- Volver al menú principal"
                ],
                'estado': 'pedidos'
            })
        elif user_input == '3':
            return menu_principal_response()  # Volver al menú principal

    # Estado por defecto: volver al menú
    return menu_principal_response()  # Volver al menú principal





def inicio_bot(request):
    return render(request, 'chatbot.html')
