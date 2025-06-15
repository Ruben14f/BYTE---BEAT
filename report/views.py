from datetime import timedelta, datetime 
from django.http import HttpResponse
from django.shortcuts import render, redirect
from orden.models import Orden, OrdenStatus
from django.contrib import messages
from django.db.models import Q
import pandas as pd
from pandas import ExcelWriter
from adminPanel.utils import *
from django.utils.timezone import now, localtime
from django.utils import formats

# Create your views here.

def orden_list_report(request):
    ordenes = Orden.objects.select_related('user').prefetch_related('productos_orden__producto').order_by('-fecha_pagada')
    orden_status = OrdenStatus.choices

    #Total de ordenes completadas
    total_completadas = total_pedidos_completados()

    #Total ordenes aun no completadas
    total_ordenes_activas = total_ordenes()

    #Total ingresos por ordenes
    total_ingresos = ingresos_totales()

    hora_actual = localtime(now()).date() 
    dia_de_la_semana = formats.date_format(hora_actual, "l")

    
    
    if 'descargar' in request.GET:
        return generar_reporte_excel(ordenes)

    return render(request, 'list_report_ordenes/reporte_orden.html', {
        'ordens': ordenes,
        'statusorden': orden_status,
        'total_ordenes' : total_ordenes_activas,
        'total_ingresos' : total_ingresos,
        'total_completadas' : total_completadas,
        'fecha_formateada': hora_actual,
        'dia_de_la_semana': dia_de_la_semana,
    })

def orden_list_filter(request):
    ordenes = Orden.objects.select_related('user').prefetch_related('productos_orden__producto').order_by('-fecha_pagada')
    orden_status = OrdenStatus.choices
    #Total de ordenes completadas
    total_completadas = total_pedidos_completados()

    #Total ordenes aun no completadas
    total_ordenes_activas = total_ordenes()

    #Total ingresos por ordenes
    total_ingresos = ingresos_totales()

    hora_actual = localtime(now()).date() 
    dia_de_la_semana = formats.date_format(hora_actual, "l")

    query_estado = request.GET.get('searchEstadoreporte')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if request.GET.get('borrarFiltro'):
        return redirect('orden_list_report')
    
    is_estado_filter = 'searchEstadoreporte' in request.GET
    is_fecha_filter = 'fecha_inicio' in request.GET and 'fecha_fin' in request.GET
    
    if not is_estado_filter and not is_fecha_filter and 'descargar' not in request.GET:
        messages.error(request, 'Debe ingresar estado para filtrar')
        return redirect('orden_list_report')

    if not is_estado_filter and not is_fecha_filter and 'descargar' not in request.GET:
        return redirect('orden_list_report')
    
    if query_estado == "None" or query_estado is None:
        query_estado = ''
        
    if query_estado and query_estado.lower() == "borrarfiltro":
        messages.success(request, 'Filtro eliminado')
        return redirect('orden_list_report')
    
    if is_estado_filter:
        if not query_estado:
            messages.error(request, 'Debe seleccionar un estado para filtrar.')
            return redirect('orden_list_report')
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
        'total_ordenes' : total_ordenes_activas,
        'total_ingresos' : total_ingresos,
        'total_completadas' : total_completadas,
        'fecha_formateada': hora_actual,
        'dia_de_la_semana': dia_de_la_semana,
    })
    
def estado_report_filter(request, ordenes, query_estado):
    orden_status = OrdenStatus.choices

    label_to_value = {
        label.lower() : value 
        for value, label in orden_status}
        
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
    data = []

    for orden in ordenes:
        for producto_orden in orden.productos_orden.all():
            data.append({
                'numero orden': f'#{orden.num_orden}',
                'cliente': f"{orden.user.first_name.capitalize()} {orden.user.last_name.capitalize()}",
                'estado': orden.get_status_display(),
                'metodo de envio': orden.get_delivery_method_display(),
                'total envio': f'${int(orden.envio_total)}',
                'total pedido': f'${int(orden.total)}',
                'fecha pedido': orden.fecha_pagada.replace(tzinfo=None).date() if orden.fecha_pagada else 'Sin fecha',
                'sku' : producto_orden.producto.sku,
                'producto': producto_orden.producto.name,
                'cantidad': producto_orden.quantity,
                'precio producto unitario' : f'${int(producto_orden.producto.price)}',
                
            })

    df = pd.DataFrame(data)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="reporte_ordenes.xlsx"'

    with ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='reporte', index=False)

    return response



