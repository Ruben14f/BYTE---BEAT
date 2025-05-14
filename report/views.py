from datetime import timedelta, datetime 
from django.shortcuts import render, redirect
from orden.models import Orden, OrdenStatus
from django.contrib import messages
from django.db.models import Q
import pandas as pd
from pandas import ExcelWriter


# Create your views here.
def orden_list_report(request):
    orden = Orden.objects.select_related('user').all().order_by('-fecha_pagada')
    orden_status = OrdenStatus.choices
    
    ruta = r'C:\Users\ruben.mansilla\Desktop\BYTE---BEAT\reporte_excel'
    datos = pd.DataFrame({
        'orden' : [o.ordenID for o in orden],
        'numero orden': [f'#{o.num_orden}' for o in orden],
        'cliente' : [f"{o.user.first_name.capitalize()} {o.user.last_name.capitalize()}" for o in orden],
        'estado': [o.get_status_display() for o in orden],
        'metodo de envio': [o.delivery_method for o in orden],
        'total envio': [f'${int(o.envio_total)}' for o in orden],
        'total pedido': [f'${int(o.total)}' for o in orden],
        'fecha pedido': [o.fecha_pagada.replace(tzinfo=None).date() if o.fecha_pagada else 'Sin fecha' for o in orden]
    })
    datos = datos[['orden','numero orden','cliente', 'estado', 'metodo de envio', 'total envio', 'total pedido', 'fecha pedido']]
    
    writer = ExcelWriter(ruta +"/reporte.xlsx" , engine='xlsxwriter')

    datos.to_excel(writer, sheet_name='reporte', index=False)

    writer.close()
    
    
    return render(request, 'list_report_ordenes/reporte_orden.html',{
        'ordens' : orden,
        'statusorden' : orden_status
    })
    
def estado_report_filter(request):
    query = request.GET.get('searchEstadoreporte')
    orden_status = OrdenStatus.choices
    print('estados disponibles vista filtro', orden_status)

    label_to_value = {
        label.lower() : value 
        for value, label in orden_status}
    print('Query buscada',query)
    print('estados disponibles vista filtro mapeado', orden_status)
    
    if query: 
        internal_value = label_to_value.get(query.lower())
        if internal_value:
            filter = Q(status__startswith=internal_value)
            order_list = Orden.objects.filter(filter).order_by('-fecha_pagada')
            print('filtro',filter)
            print('lista de ordenes',order_list)
        elif query.lower() == 'borrarfiltro':
            messages.success(request, 'Filtro eliminado')
            return redirect('orden_list_report')
    else:
        print('Query buscada',query)
        messages.error(request, 'Debe seleccionar estado para filtrar')
        return redirect('orden_list_report')
    context = {
        'ordens' : order_list,
        'queryestadoreport' : query,
        'statusorden' : orden_status
    }
    print('contexto enviado', context)

    return render(request, 'list_report_ordenes/reporte_orden.html', context)

def fecha_filter_report(request):
    ordenes = Orden.objects.all()
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    q = Q()
    print('Query buscada',q)
    print('Query buscada',fecha_inicio, fecha_fin)
    if not fecha_inicio or not fecha_fin:
        messages.error(request, 'Debe ingresar ambas fechas para filtrar.')
        return redirect('orden_list_report')
    
    if fecha_inicio:
        q &= Q(fecha_pagada__gte=fecha_inicio)
    if fecha_fin:
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
        q &= Q(fecha_pagada__lte=fecha_fin)
        
    ordenes = ordenes.filter(q).order_by('-fecha_pagada')

    if not ordenes.exists():
        messages.error(request, 'No se encontraron ordenes en esta fecha')
        return redirect('orden_list_report')
    context = {
        'ordens' : ordenes
    }
    
    return render(request, 'list_report_ordenes/reporte_orden.html', context)


def export_excel():
    ruta = r'C:\Users\ruben.mansilla\Desktop\BYTE---BEAT\reporte_excel'

    datos = pd.DataFrame({
        'id' : [1,2,3,4],
        'nombre' : ['ruben', 'maria', 'jose', 'pablo'],
        'apellido' : ['mansilla', 'perez', 'gonzalez', 'pinto'],
    })

    datos = datos[['id', 'nombre', 'apellido']]

    writer = ExcelWriter(ruta +"/reporte.xlsx" , engine='xlsxwriter')

    datos.to_excel(writer, sheet_name='reporte', index=False)

    writer.close()