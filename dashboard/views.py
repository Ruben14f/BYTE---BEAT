from django.http.response import JsonResponse
from django.shortcuts import redirect, render
from orden.models import Orden
import pandas as pd
from django.views.decorators.cache import cache_page
from django.db.models import Q
from datetime import timedelta, datetime 
from django.contrib import messages

def dashboard_view(request):

    return render(request, 'dashboard_ordens.html')

@cache_page(60 * 5) 
def get_chart(request):
    ordenes = Orden.objects.prefetch_related('productos_orden__producto').filter(fecha_pagada__isnull=False)
    print("Original:", ordenes)

    # ordenes_filtradas = filtro_fecha_dash(request, ordenes)

    # if not ordenes_filtradas.exists():
    #     print('No se encontraron órdenes con filtro, mostrando todas.')
    #     messages.error(request, 'No se encontraron órdenes en la fecha seleccionada. Mostrando todos los datos.')
    #     ordenes = ordenes 
    #     reset_filtros = True
    # else:
    #     ordenes = ordenes_filtradas
    #     reset_filtros = False

    data = []
    for orden in ordenes:
        for op in orden.productos_orden.all():
            data.append({
                'producto': op.producto.name,
                'cantidad': op.quantity,
                'fecha': orden.fecha_pagada.date() if orden.fecha_pagada else None,
            })

    df = pd.DataFrame(data)
    df_agrupado = df.groupby('producto')['cantidad'].sum().reset_index()
    print(df_agrupado)

    chart_data = []
    for _, row in df_agrupado.iterrows():
        chart_data.append({
            'value': row['cantidad'],
            'name': row['producto']
        })

    chart = {
        'tooltip': {'trigger': 'item'},
        'series': [{
            'name': 'Cantidad de productos vendidos',
            'type': 'pie',
            'radius': ['40%', '70%'],
            'center': ['50%', '70%'],
            'startAngle': 180,
            'endAngle': 360,
            'data': chart_data
        }],
        # 'resetFiltros': reset_filtros 
    }

    return JsonResponse(chart)


# def filtro_fecha_dash(request, ordenes ):
#     fecha_inicio = request.GET.get('desde')
#     fecha_fin = request.GET.get('hasta')

#     print(ordenes)

#     q = Q()

#     if fecha_inicio:
#         q &= Q(fecha_pagada__gte=fecha_inicio)
#     if fecha_fin:
#         fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d') + timedelta(days=1)
#         q &= Q(fecha_pagada__lte=fecha_fin)
        
#     ordenes = ordenes.filter(q)
    

    
#     print(ordenes,'filtro realizado?')
#     return ordenes
