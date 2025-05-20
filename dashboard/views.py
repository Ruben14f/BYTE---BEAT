from django.http.response import JsonResponse
from django.shortcuts import render
from orden.models import Orden
import pandas as pd
from django.views.decorators.cache import cache_page
from datetime import datetime 
from django.core.cache import cache
from datetime import datetime, timedelta, time
from django.utils.timezone import now, make_aware 

def dashboard_view(request):
    return render(request, 'dashboard_ordens.html')

#@cache_page(60 * 5) 
def get_chart(request):
    # cache_key = 'dashboard_chart_data_pie'
    # chart_json = cache.get(cache_key)
    # if chart_json:
    #     return JsonResponse(chart_json)
    
    start_datetime, end_datetime = get_date_range(request)

    ordenes = Orden.objects.prefetch_related('productos_orden__producto').filter(
        fecha_pagada__gte=start_datetime,
        fecha_pagada__lte=end_datetime,
        fecha_pagada__isnull=False
    )

    print("Original:", ordenes)
    data = []
    for orden in ordenes:
        for op in orden.productos_orden.all():
            data.append({
                'producto': op.producto.name,
                'cantidad': op.quantity,
                'fecha': orden.fecha_pagada.date() if orden.fecha_pagada else None,
            })
    df = pd.DataFrame(data)
    if df.empty:
        return JsonResponse({
            'tooltip': {'trigger': 'item'},
            'series': []
        })
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
    }

    # cache.set(cache_key, chart, 300)
    return JsonResponse(chart)

#@cache_page(60 * 5)
def get_chart2(request):
    # cache_key = 'dashboard_chart_data_bars'
    # chart_json = cache.get(cache_key)
    # if chart_json:
    #     return JsonResponse(chart_json)

    start_datetime, end_datetime = get_date_range(request)

    ordenes = Orden.objects.prefetch_related('productos_orden__producto').filter(
        fecha_pagada__gte=start_datetime,
        fecha_pagada__lte=end_datetime,
        fecha_pagada__isnull=False
    )

    data = []
    for orden in ordenes:
        for op in orden.productos_orden.all():
            precio_unitario = float(op.producto.price) if op.producto.price else 0
            valor_venta = precio_unitario * op.quantity
            print(f"Producto: {op.producto.name}, Precio: {precio_unitario}, Cantidad: {op.quantity}, Valor venta: {valor_venta}")
            categoria = op.producto.category.name if op.producto.category else 'Sin categoria'
            mes = orden.fecha_pagada.month if orden.fecha_pagada else None
            anio = orden.fecha_pagada.year if orden.fecha_pagada else None

            data.append({
                'categoria': categoria,
                'valor': valor_venta,
                'mes': mes,
                'anio': anio,
            })

    df = pd.DataFrame(data)

    if df.empty:
        return JsonResponse({
            'xAxis': {'data': []},
            'series': []
        })

    año_actual = datetime.now().year
    df = df[df['anio'] == año_actual]

    pivot_df = df.pivot_table(index='mes', columns='categoria', values='valor', aggfunc='sum', fill_value=0)

    meses = list(range(1, 13))
    pivot_df = pivot_df.reindex(meses, fill_value=0)
    meses_nombre = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul']

    series = []
    for categoria in pivot_df.columns:
        valores = pivot_df[categoria].astype(float).tolist()
        series.append({
            'name': categoria,
            'type': 'bar',
            'data': valores,
        })

    option = {
        'tooltip': {'trigger': 'axis'},
        'legend': {'data': list(pivot_df.columns)},
        'xAxis': {
            'type': 'category',
            'data': meses_nombre
        },
        'yAxis': {
            'type': 'value',
            'name': 'Ventas (Pesos)'
        },
        'series': series
    }

    # cache.set(cache_key, option, 300)

    return JsonResponse(option)

#@cache_page(60 * 5)
def get_chart3(request):
    start_datetime, end_datetime = get_date_range(request)

    ordenes = Orden.objects.prefetch_related('productos_orden__producto').filter(
        fecha_pagada__gte=start_datetime,
        fecha_pagada__lte=end_datetime,
        fecha_pagada__isnull=False
    )   

    data = []
    for orden in ordenes:
        for op in orden.productos_orden.all():
            precio_unitario = float(op.producto.price) if op.producto.price else 0
            valor_venta = precio_unitario * op.quantity
            categoria = op.producto.category.name if op.producto.category else 'Sin categoria'
            mes = orden.fecha_pagada.month if orden.fecha_pagada else None

            data.append({
                'categoria': categoria,
                'valor': valor_venta,
                'mes': mes,
            })

    df = pd.DataFrame(data)

    if df.empty:
        # Retornar estructura vacía para evitar errores
        return JsonResponse({
            'legend': {'data': []},
            'tooltip': {'trigger': 'axis', 'showContent': True},
            'dataset': {'source': []},
            'xAxis': {'type': 'category'},
            'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
            'series': []
        })

    # Forzar tipo float
    df['valor'] = df['valor'].astype(float)

    # Agrupar sumando valor por categoria y mes
    df_agrupado = df.groupby(['categoria', 'mes'])['valor'].sum().reset_index()

    meses_nombre = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul']
    categorias = df_agrupado['categoria'].unique()

    header = ['category'] + meses_nombre
    rows = []

    for categoria in categorias:
        fila = [categoria]
        for i in range(1, 13):
            filtro = df_agrupado[(df_agrupado['categoria'] == categoria) & (df_agrupado['mes'] == i)]
            if not filtro.empty:
                fila.append(round(float(filtro['valor'].values[0]), 2))
            else:
                fila.append(0)
        rows.append(fila)

    dataset_source = [header] + rows

    chart = {
        'legend': {'data': list(categorias)},
        'tooltip': {'trigger': 'axis', 'showContent': True},
        'dataset': {'source': dataset_source},
        'xAxis': {'type': 'category'},
        'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
        'series': [
            {
                'type': 'line',
                'smooth': True,
                'seriesLayoutBy': 'row',
                'emphasis': {'focus': 'series'}
            } for _ in categorias
        ],
    }

    return JsonResponse(chart)

def get_chart4(request):
    start_datetime, end_datetime = get_date_range(request)

    ordenes = Orden.objects.prefetch_related('productos_orden__producto').filter(
        fecha_pagada__gte=start_datetime,
        fecha_pagada__lte=end_datetime,
        fecha_pagada__isnull=False
    )

    data = []
    for orden in ordenes:
        for op in orden.productos_orden.all():
            data.append({
                'producto': op.producto.name,
                'cantidad': op.quantity,
                'fecha': orden.fecha_pagada.date() if orden.fecha_pagada else None,
            })

    df = pd.DataFrame(data)
    if df.empty:
        return JsonResponse({
            'tooltip': {'trigger': 'item'},
            'series': []
        })
    df_agrupado = df.groupby('producto')['cantidad'].sum().reset_index()

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
            'avoidLabelOverlap': False,
            'label': {
                'show': True,           
                'position': 'outside',   
                'formatter': '{b}: {d}%',
                'fontWeight': 'bold',
            },
            'labelLine': {
                'show': True,           
                'length': 15,
                'length2': 10
            },
            'itemStyle': {
            'borderColor': '#fff',
            'borderWidth': 4       
            },
            'data': chart_data,
        }],
    }

    return JsonResponse(chart)




def get_date_range(request):
    range_type = request.GET.get('range', None)
    start_date_str = request.GET.get('start_date', None)
    end_date_str = request.GET.get('end_date', None)
    today = now().date()

    # Primero definir start_date y end_date según el filtro
    if not range_type and not (start_date_str and end_date_str):
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif range_type == 'today':
        start_date = end_date = today
    elif range_type == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif range_type == 'month':
        start_date = today.replace(day=1)
        end_date = today
    elif range_type == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today
    elif start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            start_date = today.replace(month=1, day=1)
            end_date = today
    else:
        start_date = today.replace(month=1, day=1)
        end_date = today

    # Ahora sí, combinar fecha y hora para obtener datetime
    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)

    # Convertir a aware para que coincida con campo con zona horaria
    start_datetime = make_aware(start_datetime)
    end_datetime = make_aware(end_datetime)

    return start_datetime, end_datetime