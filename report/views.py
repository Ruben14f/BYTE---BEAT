from datetime import timedelta, datetime 
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from orden.models import Orden, OrdenStatus
from django.contrib import messages
from django.db.models import Q
import pandas as pd
from pandas import ExcelWriter


# Create your views here.

def orden_list_report(request):
    ordenes = Orden.objects.select_related('user').all().order_by('-fecha_pagada')
    orden_status = OrdenStatus.choices
    
    if 'descargar' in request.GET:
        return generar_reporte_excel(ordenes)

    return render(request, 'list_report_ordenes/reporte_orden.html', {
        'ordens': ordenes,
        'statusorden': orden_status,
    })

def orden_list_filter(request):
    ordenes = Orden.objects.select_related('user').all().order_by('-fecha_pagada')
    orden_status = OrdenStatus.choices
    query_estado = request.GET.get('searchEstadoreporte')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if request.GET.get('borrarFiltro'):
        return redirect('orden_list_report')
    
    is_estado_filter = 'searchEstadoreporte' in request.GET
    is_fecha_filter = 'fecha_inicio' in request.GET and 'fecha_fin' in request.GET
    
    if not is_estado_filter and not is_fecha_filter and 'descargar' not in request.GET:
        return generar_reporte_excel(ordenes)

    if not is_estado_filter and not is_fecha_filter and 'descargar' not in request.GET:
        return redirect('orden_list_report')
    
    if query_estado == "None" or query_estado is None:
        query_estado = ''
        
    if query_estado and query_estado.lower() == "borrarfiltro":
        messages.success(request, 'Filtro eliminado')
        return redirect('orden_list_report')
    
    if is_estado_filter:
        # if not query_estado:
        #     messages.error(request, 'Debe seleccionar un estado para filtrar.')
        #     return redirect('orden_list_report')
        try:
            ordenes = estado_report_filter(request, ordenes, query_estado)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('orden_list_report')
        
    if is_fecha_filter:
        if not fecha_inicio or not fecha_fin:
            messages.error(request, 'Debe ingresar ambas fechas para filtrar.')
            return redirect('orden_list_report')
        try:
            if fecha_inicio:
                datetime.strptime(fecha_inicio, '%Y-%m-%d')
            if fecha_fin:
                datetime.strptime(fecha_fin, '%Y-%m-%d')
                
            ordenes = fecha_filter_report(request, ordenes, fecha_inicio, fecha_fin)
            
            if ordenes is None:
                return redirect('orden_list_report')
        except ValueError:
            messages.error(request, 'Formato de fecha inválido.')
            return redirect('orden_list_report')



    if 'descargar' in request.GET:
        return generar_reporte_excel(ordenes) 


    return render(request, 'list_report_ordenes/reporte_orden_filtrados.html', {
        'ordens': ordenes,
        'statusorden': orden_status,
        'queryestadoreport': query_estado,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
    })
    

def estado_report_filter(request, ordenes, query_estado):
    orden_status = OrdenStatus.choices

    label_to_value = {
        label.lower() : value 
        for value, label in orden_status}
    print('Query buscada',query_estado)
    # if query_estado is None:
    #     messages.error(request, 'Debe seleccionar un estado para filtrar.')
    #     return redirect('orden_list_report')
    
    internal_value = label_to_value.get(query_estado.lower())
    if internal_value:
        filter = Q(status__startswith=internal_value)
        ordenes = ordenes.filter(filter)
    else:
        messages.error(request, 'Estado inválido seleccionado.')
        return redirect('orden_list_report')

    return ordenes


# Filtro por fecha
def fecha_filter_report(request, ordenes, fecha_inicio, fecha_fin):
    q = Q()

    if fecha_inicio:
        q &= Q(fecha_pagada__gte=fecha_inicio)
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
        q &= Q(fecha_pagada__lte=fecha_fin)
        
    ordenes = ordenes.filter(q).order_by('-fecha_pagada')
    if not ordenes.exists():
        messages.error(request, 'No se encontraron órdenes en esta fecha')
        return None
    return ordenes

def generar_reporte_excel(ordenes):
    datos = pd.DataFrame({
        'orden': [o.ordenID for o in ordenes],
        'numero orden': [f'#{o.num_orden}' for o in ordenes],
        'cliente': [f"{o.user.first_name.capitalize()} {o.user.last_name.capitalize()}" for o in ordenes],
        'estado': [o.get_status_display() for o in ordenes],
        'metodo de envio': [o.get_delivery_method_display() for o in ordenes],
        'total envio': [f'${int(o.envio_total)}' for o in ordenes],
        'total pedido': [f'${int(o.total)}' for o in ordenes],
        'fecha pedido': [o.fecha_pagada.replace(tzinfo=None).date() if o.fecha_pagada else 'Sin fecha' for o in ordenes]
    })

    datos = datos[['orden', 'numero orden', 'cliente', 'estado', 'metodo de envio', 'total envio', 'total pedido', 'fecha pedido']]
    
    # Crear el archivo Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_ordenes.xlsx"'

    with ExcelWriter(response, engine='xlsxwriter') as writer:
        datos.to_excel(writer, sheet_name='reporte', index=False)

    return response

# def estado_report_filter(request):
#     query = request.GET.get('searchEstadoreporte')
#     orden_status = OrdenStatus.choices
#     print('estados disponibles vista filtro', orden_status)

#     label_to_value = {
#         label.lower() : value 
#         for value, label in orden_status}
#     print('Query buscada',query)
#     print('estados disponibles vista filtro mapeado', orden_status)
    
#     if query: 
#         internal_value = label_to_value.get(query.lower())
#         if internal_value:
#             filter = Q(status__startswith=internal_value)
#             order_list = Orden.objects.filter(filter).order_by('-fecha_pagada')
#             print('filtro',filter)
#             print('lista de ordenes',order_list)
#         elif query.lower() == 'borrarfiltro':
#             messages.success(request, 'Filtro eliminado') -> AGREGAR ESTA VALIDACION 2
#             return redirect('orden_list_report')
#     else:
#         print('Query buscada',query)
#         messages.error(request, 'Debe seleccionar estado para filtrar') - AGREGAR ESTA VALIDACION 1
#         return redirect('orden_list_report')
#     context = {
#         'ordens' : order_list,
#         'queryestadoreport' : query,
#         'statusorden' : orden_status
#     }
#     print('contexto enviado', context)

#     return render(request, 'list_report_ordenes/reporte_orden.html', context)

# def fecha_filter_report(request):
#     ordenes = Orden.objects.all()
#     fecha_inicio = request.GET.get('fecha_inicio')
#     fecha_fin = request.GET.get('fecha_fin')
#     q = Q()
#     print('Query buscada',q)
#     print('Query buscada',fecha_inicio, fecha_fin)
#     if not fecha_inicio or not fecha_fin:
#         messages.error(request, 'Debe ingresar ambas fechas para filtrar.') -> AGREGAR ESTA VALIDACION 3
#         return redirect('orden_list_report')
    
#     if fecha_inicio:
#         q &= Q(fecha_pagada__gte=fecha_inicio)
#     if fecha_fin:
#         fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
#         q &= Q(fecha_pagada__lte=fecha_fin)
        
#     ordenes = ordenes.filter(q).order_by('-fecha_pagada')

#     if not ordenes.exists():
#         messages.error(request, 'No se encontraron ordenes en esta fecha')
#         return redirect('orden_list_report')
#     context = {
#         'ordens' : ordenes
#     }
    
#     return render(request, 'list_report_ordenes/reporte_orden.html', context)

