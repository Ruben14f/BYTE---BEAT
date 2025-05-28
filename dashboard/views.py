from django.http.response import JsonResponse
from django.shortcuts import render
from orden.models import Orden
import pandas as pd
from datetime import datetime 
from datetime import datetime, timedelta, time
from django.utils.timezone import now, make_aware
from datetime import timezone
import calendar

def dashboard_view(request):
    return render(request, 'dashboard_ordens.html')

#grafico de barras
def get_chart2(request):
    # Obtener filtro general
    filtro_global = request.GET.get('range', None)
    # Obtener filtro individual para este gráfico
    filtro_individual = request.GET.get('range_chart2', None)

    # Por defecto usar filtro global para fechas
    start_datetime, end_datetime = get_date_range(request)

    # Si hay filtro individual para este gráfico, usarlo para rango de fechas
    if filtro_individual:
        start_datetime, end_datetime = get_date_range_individual(request, 'range_chart2')
        rango = filtro_individual
    else:
        rango = filtro_global

    # Ajustar rango para comparación anual sin perder filtro global
    if filtro_individual == 'comparativa_anio':
        # Expandir rango para traer años completos anteriores y actuales según filtro global
        start_datetime = start_datetime.replace(year=start_datetime.year - 1, month=1, day=1)
        end_datetime = end_datetime.replace(month=12, day=31)
    elif filtro_individual == 'comparativa_mes':
        pass

    # Consultar con rango ajustado
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
            anio = orden.fecha_pagada.year if orden.fecha_pagada else None

            data.append({
                'categoria': categoria,
                'valor': valor_venta,
                'mes': mes,
                'anio': anio,
            })

    df = pd.DataFrame(data)

    # Si filtro individual es de comparativa, usar función especial sin alterar lógica global
    if filtro_individual == 'comparativa_anio':
        return JsonResponse(generar_comparativa(df, tipo='anio'))
    elif filtro_individual == 'comparativa_mes':
        return JsonResponse(generar_comparativa(df, tipo='mes'))

    # Si no hay datos
    if df.empty:
        option = {
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': ['Sin datos']},
            'xAxis': {
                'type': 'category',
                'data': ['Sin datos'],
                'name': 'Meses'
            },
            'yAxis': {
                'type': 'value',
                'name': 'Ventas (Pesos)'
            },
            'series': [{
                'name': 'Sin datos',
                'type': 'bar',
                'data': [0],
            }]
        }
        return JsonResponse(option)

    nombres_meses_completos = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                               'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    if rango == 'year':
        meses = list(range(1, 13))
    else:
        months_diff = (end_datetime.year - start_datetime.year) * 12 + (end_datetime.month - start_datetime.month) + 2
        last_month = min(start_datetime.month + months_diff - 1, 12)
        meses = list(range(start_datetime.month, last_month + 1))

    meses_nombre = [nombres_meses_completos[m - 1] for m in meses]

    pivot_df = df.pivot_table(index='mes', columns='categoria', values='valor', aggfunc='sum', fill_value=0)
    pivot_df = pivot_df.reindex(meses, fill_value=0)

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
            'data': meses_nombre,
            'name': 'Meses',
            'axisLabel': {'interval': 0}
        },
        'yAxis': {
            'type': 'value',
            'name': 'Ventas (Pesos)'
        },
        'series': series
    }

    return JsonResponse(option)

    # Mantener lógica original de filtro global para rango y meses
    nombres_meses_completos = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                               'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

    if rango == 'year':
        meses = list(range(1, 13))
    else:
        months_diff = (end_datetime.year - start_datetime.year) * 12 + (end_datetime.month - start_datetime.month) + 2
        last_month = min(start_datetime.month + months_diff - 1, 12)
        meses = list(range(start_datetime.month, last_month + 1))

    meses_nombre = [nombres_meses_completos[m - 1] for m in meses]

    pivot_df = df.pivot_table(index='mes', columns='categoria', values='valor', aggfunc='sum', fill_value=0)
    pivot_df = pivot_df.reindex(meses, fill_value=0)

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
            'data': meses_nombre,
            'name': 'Meses',
            'axisLabel': {'interval': 0}
        },
        'yAxis': {
            'type': 'value',
            'name': 'Ventas (Pesos)'
        },
        'series': series
    }

    return JsonResponse(option)




#grafico de lineas
def get_chart3(request):
    start_datetime, end_datetime = get_date_range(request)
    filtro_individual = request.GET.get('range_chart3', None)
    print(filtro_individual)
    print('invidual antes de if',filtro_individual)
    
    if filtro_individual:
        start_datetime, end_datetime = get_date_range_individual(request,'range_chart3')
        rango = filtro_individual
        print('invidual antes de if',rango)
    else:
        start_datetime, end_datetime = get_date_range(request)
        rango = request.GET.get('range', None)

    months_diff = (end_datetime.year - start_datetime.year) * 12 + (end_datetime.month - start_datetime.month) + 2

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
        meses = list(range(start_datetime.month, min(start_datetime.month + months_diff, 13)))
        nombres_meses_completos = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                                   'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
        meses_nombre = [nombres_meses_completos[m-1] for m in meses]

        option = {
            'legend': {'data': ['Sin datos']},
            'tooltip': {'trigger': 'axis', 'showContent': True},
            'dataset': {'source': [['category'] + meses_nombre, ['Sin datos'] + [0]*len(meses_nombre)]},
            'xAxis': {'type': 'category', 'name': 'Meses'},
            'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
            'series': [{
                'type': 'line',
                'smooth': True,
                'seriesLayoutBy': 'row',
                'emphasis': {'focus': 'series'}
            }]
        }
        return JsonResponse(option)

    df['valor'] = df['valor'].astype(float)
    df_agrupado = df.groupby(['categoria', 'mes'])['valor'].sum().reset_index()

    # Calcular meses a mostrar (últimos N según rango)
    last_month = min(start_datetime.month + months_diff - 1, 12)
    meses = list(range(start_datetime.month, last_month + 1))

    nombres_meses_completos = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                               'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
    meses_nombre = [nombres_meses_completos[m-1] for m in meses]

    categorias = df_agrupado['categoria'].unique()

    header = ['category'] + meses_nombre
    rows = []

    for categoria in categorias:
        fila = [categoria]
        for m in meses:
            filtro = df_agrupado[(df_agrupado['categoria'] == categoria) & (df_agrupado['mes'] == m)]
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
        'xAxis': {'type': 'category', 'name': 'Meses'},
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

#grafico de torta
def get_chart4(request):
    start_datetime, end_datetime = get_date_range(request)
    filtro_individual = request.GET.get('range_chart4', None)
    print(filtro_individual)
    print('invidual antes de if',filtro_individual)
    
    if filtro_individual:
        start_datetime, end_datetime = get_date_range_individual(request,'range_chart4')
        rango = filtro_individual
        print('invidual antes de if',rango)
    else:
        start_datetime, end_datetime = get_date_range(request)
        rango = request.GET.get('range', None)
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
        chart_data = [{
            'value': 0,
            'name': 'Sin datos'
        }]
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



#filtro para todo el dashboard
def get_date_range(request):
    range_type = request.GET.get('range', None)
    print('rango desde funcion get:date',range_type)
    
    today = now().date()

    if not range_type or range_type == '':
        six_months_ago = today - timedelta(days=180)
        if six_months_ago.year < today.year:
            start_date = today.replace(month=1, day=1)
        else:
            start_date = six_months_ago.replace(day=1)
        end_date = today
    elif range_type == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    elif range_type == 'today':
        start_date = end_date = today
    elif range_type == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif range_type == 'month':
        start_date = today.replace(day=1)
        end_date = today
    else:
        start_date = today.replace(month=1, day=1)
        end_date = today

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)
    start_datetime = make_aware(start_datetime).astimezone(timezone.utc)
    end_datetime = make_aware(end_datetime).astimezone(timezone.utc)

    return start_datetime, end_datetime


def get_date_range_individual(request, param_name):
    range_type = request.GET.get(param_name, None)
    today = now().date()

    if not range_type or range_type == '':
        six_months_ago = today - timedelta(days=180)
        if six_months_ago.year < today.year:
            start_date = today.replace(month=1, day=1)
        else:
            start_date = six_months_ago.replace(day=1)
        end_date = today
    elif range_type == 'year':
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    elif range_type == '7days':
        start_date = today - timedelta(days=7)
        end_date = today
    elif range_type == '30days':
        start_date = today - timedelta(days=30)
        end_date = today
    else:
        start_date = today.replace(month=1, day=1)
        end_date = today

    start_datetime = datetime.combine(start_date, time.min)
    end_datetime = datetime.combine(end_date, time.max)
    start_datetime = make_aware(start_datetime).astimezone(timezone.utc)
    end_datetime = make_aware(end_datetime).astimezone(timezone.utc)
    return start_datetime, end_datetime


def generar_comparativa(df, tipo='anio'):
    if df.empty or 'anio' not in df.columns or 'mes' not in df.columns:
        return {
            'tooltip': {'trigger': 'axis'},
            'legend': {'data': ['Sin datos']},
            'xAxis': {'type': 'category', 'data': ['Sin datos'], 'name': 'Meses'},
            'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
            'series': [{'name': 'Sin datos', 'type': 'bar', 'data': [0]}]
        }

    if tipo == 'anio':
        # Agrupar por categoría y año
        pivot = df.pivot_table(index='categoria', columns='anio', values='valor', aggfunc='sum', fill_value=0)
        pivot = pivot.sort_index()

        # Construir dimensions (primera columna es "Producto")
        dimensiones = ['Producto'] + [str(col) for col in pivot.columns]

        # Construir source como lista de diccionarios
        source = []
        for categoria, fila in pivot.iterrows():
            fila_dict = {'Producto': categoria}
            for anio, valor in fila.items():
                fila_dict[str(anio)] = float(valor)
            source.append(fila_dict)

        option = {
            'legend': {},
            'tooltip': {},
            'dataset': {
                'dimensions': dimensiones,
                'source': source
            },
            'xAxis': { 'type': 'category' },
            'yAxis': {},
            'series': [ { 'type': 'bar' } for _ in dimensiones[1:] ]
        }

        return option

    elif tipo == 'mes':
        agrupado = df.groupby(['anio', 'mes', 'categoria'])['valor'].sum().reset_index()

        meses_ordenados = agrupado[['anio', 'mes']].drop_duplicates().sort_values(['anio', 'mes'], ascending=False)
        meses_comparar = meses_ordenados.head(2).values.tolist()
        if len(meses_comparar) < 2:
            return {
                'tooltip': {'trigger': 'axis'},
                'legend': {'data': ['Sin datos']},
                'xAxis': {'type': 'category', 'data': ['Sin datos'], 'name': 'Meses'},
                'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
                'series': [{'name': 'Sin datos', 'type': 'bar', 'data': [0]}]
            }

        agrupado['label'] = agrupado.apply(lambda r: f'{calendar.month_abbr[r["mes"]]} {r["anio"]}', axis=1)
        pivot = agrupado[
            agrupado[['anio', 'mes']].apply(tuple, axis=1).isin(meses_comparar)
        ].pivot_table(index='categoria', columns='label', values='valor', aggfunc='sum', fill_value=0)
        pivot = pivot.sort_index()

        dimensiones = ['Producto'] + [str(c) for c in pivot.columns]

        source = []
        for categoria, fila in pivot.iterrows():
            fila_dict = {'Producto': categoria}
            for etiqueta, valor in fila.items():
                fila_dict[str(etiqueta)] = float(valor)
            source.append(fila_dict)

        option = {
            'legend': {},
            'tooltip': {},
            'dataset': {
                'dimensions': dimensiones,
                'source': source
            },
            'xAxis': { 'type': 'category' },
            'yAxis': {},
            'series': [ { 'type': 'bar' } for _ in dimensiones[1:] ]
        }

        return option

    return {
        'tooltip': {'trigger': 'axis'},
        'legend': {'data': ['Sin datos']},
        'xAxis': {'type': 'category', 'data': ['Sin datos'], 'name': 'Meses'},
        'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
        'series': [{'name': 'Sin datos', 'type': 'bar', 'data': [0]}]
    }