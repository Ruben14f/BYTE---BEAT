from django.http.response import JsonResponse
from django.shortcuts import render
from orden.models import Orden
import pandas as pd
from datetime import datetime, timedelta, time,timezone
from django.utils.timezone import now, make_aware
import calendar
import locale

#Mes, Dias en español de importacion calendar
locale.setlocale(locale.LC_TIME, 'Spanish_Spain')

def dashboard_view(request):
    return render(request, 'dashboard_ordens.html')

#Grafico de barras
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
        print(filtro_individual, 'comparativa año?')
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
        fecha_dia = orden.fecha_pagada.date() if orden.fecha_pagada else None
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
                'fecha_dia': fecha_dia,  
            })

    df = pd.DataFrame(data)

    # Comparativas especiales
    if filtro_individual == 'comparativa_anio':
        print('comparativa_anio que retorna el jsonresponse ', filtro_individual)
        return JsonResponse(generar_comparativa_barras(df, tipo='anio'))
    elif filtro_individual == 'comparativa_mes':
        return JsonResponse(generar_comparativa_barras(df, tipo='mes'))

    # Sin datos
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

    if rango == '7days':
        # Mostrar por días individuales (igual que antes)
        num_days = 7
        fechas = [end_datetime.date() - timedelta(days=i) for i in range(num_days)]
        fechas.reverse()  # orden cronológico

        dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        nombres_dias = [f"{dias_semana[fecha.weekday()]} {fecha.day}" for fecha in fechas]

        pivot_df = df.pivot_table(index='fecha_dia', columns='categoria', values='valor', aggfunc='sum', fill_value=0)
        pivot_df = pivot_df.reindex(fechas, fill_value=0)

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
            'toolbox': {
                'show': True,
                'feature': {
                    'saveAsImage': {
                        'title': 'Guardar imagen',
                        'name' :'grafico_ventas'
                    }
                }
            },
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

    elif rango == '30days':
        # Mostrar por semanas (agrupación semanal)
        df['semana'] = df['fecha_dia'].apply(lambda x: x.isocalendar()[1] if pd.notnull(x) else None)

        # Crear rango de semanas cubriendo el período completo
        semana_inicio = start_datetime.date().isocalendar()[1]
        semana_fin = end_datetime.date().isocalendar()[1]

        if semana_fin < semana_inicio:
            semanas = list(range(semana_inicio, 53 + 1)) + list(range(1, semana_fin + 1))
        else:
            semanas = list(range(semana_inicio, semana_fin + 1))

        # Para mostrar etiquetas legibles con rango de fechas de cada semana
        nombres_semanas = []
        for sem in semanas:
            # Para evitar complejidad con años diferentes, se puede simplificar:
            try:
                anyo = start_datetime.year
                # Ajustar año si semanas están en el año siguiente
                if sem < semana_inicio:
                    anyo = start_datetime.year + 1

                lunes_semana = pd.Timestamp.fromisocalendar(anyo, sem, 1).date()
                domingo_semana = pd.Timestamp.fromisocalendar(anyo, sem, 7).date()
                nombres_semanas.append(f"{lunes_semana.strftime('%d/%m')} - {domingo_semana.strftime('%d/%m')}")
            except Exception:
                # En caso de error usar sólo número de semana
                nombres_semanas.append(f"Semana {sem}")

        pivot_df = df.pivot_table(index='semana', columns='categoria', values='valor', aggfunc='sum', fill_value=0)
        pivot_df = pivot_df.reindex(semanas, fill_value=0)

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
            'toolbox': {
                'show': True,
                'feature': {
                    'saveAsImage': {
                        'title': 'Guardar imagen',
                        'name' :'grafico_ventas'
                    }
                }
            },
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
        'toolbox': {
            'show': True,
            'feature': {
                'saveAsImage': {
                    'title': 'Guardar imagen',
                    'name' :'grafico_ventas'
                }
            }
        },
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

#Grafico de lineas
def get_chart3(request):
    start_datetime, end_datetime = get_date_range(request)
    filtro_individual = request.GET.get('range_chart3', None)
    print(filtro_individual)
    print('invidual antes de if', filtro_individual)
    
    if filtro_individual:
        start_datetime, end_datetime = get_date_range_individual(request, 'range_chart3')
        rango = filtro_individual
        print('invidual antes de if', rango)

        if filtro_individual == 'comparativa_anio':
            current_year = end_datetime.year
            start_datetime = start_datetime.replace(year=current_year - 1, month=1, day=1, hour=0, minute=0, second=0)
            end_datetime = end_datetime.replace(year=current_year, month=12, day=31, hour=23, minute=59, second=59)

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
            fecha_dia = orden.fecha_pagada.date() if orden.fecha_pagada else None
            mes = orden.fecha_pagada.month if orden.fecha_pagada else None
            anio = orden.fecha_pagada.year if orden.fecha_pagada else None

            data.append({
                'categoria': categoria,
                'valor': valor_venta,
                'fecha_dia': fecha_dia,
                'mes': mes,
                'anio': anio,
            })

    df = pd.DataFrame(data)

    if filtro_individual == 'comparativa_anio':
        return JsonResponse(generar_comparativa_lineas(df, tipo='anio'))
    elif filtro_individual == 'comparativa_mes':
        return JsonResponse(generar_comparativa_lineas(df, tipo='mes'))

    if df.empty:
        option = {
            'legend': {'data': ['Sin datos']},
            'tooltip': {'trigger': 'axis', 'showContent': True},
            'dataset': {'source': [['category', 'Sin datos'], ['Sin datos', 0]]},
            'xAxis': {'type': 'category', 'name': 'Fecha'},
            'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
            'series': [{
                'type': 'line',
                'smooth': True,
                'seriesLayoutBy': 'row',
                'emphasis': {'focus': 'series'}
            }]
        }
        return JsonResponse(option)

    if rango == '7days':
        num_days = 7
        fechas = [end_datetime.date() - timedelta(days=i) for i in range(num_days)]
        fechas.reverse()

        dias_semana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
        nombres_dias = [f"{dias_semana[fecha.weekday()]} {fecha.day}" for fecha in fechas]

        pivot_df = df.pivot_table(index='fecha_dia', columns='categoria', values='valor', aggfunc='sum', fill_value=0)
        pivot_df = pivot_df.reindex(fechas, fill_value=0)

        series = []
        for categoria in pivot_df.columns:
            valores = pivot_df[categoria].astype(float).tolist()
            series.append({
                'name': categoria,
                'type': 'line',
                'smooth': True,
                'data': valores,
            })

        option = {
            'legend': {'data': list(pivot_df.columns)},
            'toolbox': {
                'show': True,
                'feature': {
                    'saveAsImage': {
                        'title': 'Guardar imagen',
                        'name' :'grafico_ventas'
                    }
                }
            },
            'tooltip': {'trigger': 'axis', 'showContent': True},
            'xAxis': {
                'type': 'category',
                'data': nombres_dias,
                'name': 'Días',
                'axisLabel': {'interval': 0}
            },
            'yAxis': {
                'type': 'value',
                'name': 'Ventas (Pesos)'
            },
            'series': series
        }
        return JsonResponse(option)

    elif rango == '30days':
        df['semana'] = df['fecha_dia'].apply(lambda x: x.isocalendar()[1] if pd.notnull(x) else None)

        semana_inicio = start_datetime.date().isocalendar()[1]
        semana_fin = end_datetime.date().isocalendar()[1]

        if semana_fin < semana_inicio:
            semanas = list(range(semana_inicio, 53 + 1)) + list(range(1, semana_fin + 1))
        else:
            semanas = list(range(semana_inicio, semana_fin + 1))

        nombres_semanas = []
        for sem in semanas:
            try:
                anyo = start_datetime.year
                if sem < semana_inicio:
                    anyo += 1
                lunes_semana = pd.Timestamp.fromisocalendar(anyo, sem, 1).date()
                domingo_semana = pd.Timestamp.fromisocalendar(anyo, sem, 7).date()
                nombres_semanas.append(f"{lunes_semana.strftime('%d/%m')} - {domingo_semana.strftime('%d/%m')}")
            except Exception:
                nombres_semanas.append(f"Semana {sem}")

        pivot_df = df.pivot_table(index='semana', columns='categoria', values='valor', aggfunc='sum', fill_value=0)
        pivot_df = pivot_df.reindex(semanas, fill_value=0)

        series = []
        for categoria in pivot_df.columns:
            valores = pivot_df[categoria].astype(float).tolist()
            series.append({
                'name': categoria,
                'type': 'line',
                'smooth': True,
                'data': valores,
            })

        option = {
            'legend': {'data': list(pivot_df.columns)},
            'toolbox': {
                'show': True,
                'feature': {
                    'saveAsImage': {
                        'title': 'Guardar imagen',
                        'name' :'grafico_ventas'
                    }
                }
            },
            'tooltip': {'trigger': 'axis', 'showContent': True},
            'xAxis': {
                'type': 'category',
                'data': nombres_semanas,
                'name': 'Semanas',
                'axisLabel': {'interval': 0, 'rotate': 30}
            },
            'yAxis': {
                'type': 'value',
                'name': 'Ventas (Pesos)'
            },
            'series': series
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

    header = ['category'] + meses_nombre
    rows = []
    for categoria in pivot_df.columns:
        fila = [categoria]
        for m in meses:
            fila.append(float(pivot_df.at[m, categoria]))
        rows.append(fila)

    dataset_source = [header] + rows

    option = {
        'legend': {'data': list(pivot_df.columns)},
        'toolbox': {
            'show': True,
            'feature': {
                'saveAsImage': {
                    'title': 'Guardar imagen',
                    'name' :'grafico_ventas'
                }
            }
        },
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
            } for _ in pivot_df.columns
        ]
    }
    return JsonResponse(option)

#grafico de torta
def get_chart4(request):
    start_datetime, end_datetime = get_date_range(request)
    filtro_individual = request.GET.get('range_chart4', None)
    top_filter = request.GET.get('top_filter_chart4', 'all')  # Leer filtro top, por defecto 'all'
    
    print(filtro_individual)
    print('individual antes de if', filtro_individual)
    print('top_filter:', top_filter)
    
    if filtro_individual:
        start_datetime, end_datetime = get_date_range_individual(request, 'range_chart4')
        rango = filtro_individual
        print('individual después de if', rango)
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
    else:
        df_agrupado = df.groupby('producto')['cantidad'].sum().reset_index()

        # Aplicar filtro top según selección
        if top_filter == 'top5':
            df_agrupado = df_agrupado.nlargest(5, 'cantidad')
        elif top_filter == 'top10':
            df_agrupado = df_agrupado.nlargest(10, 'cantidad')
        elif top_filter == 'less5':
            df_agrupado = df_agrupado.nsmallest(5, 'cantidad')
        # else 'all' deja todo sin filtrar
    
        chart_data = [{'value': row['cantidad'], 'name': row['producto']} for _, row in df_agrupado.iterrows()]
    
    chart = {
        'tooltip': {'trigger': 'item'},
        'toolbox': {
            'show': True,
            'feature': {
                'saveAsImage': {
                    'title': 'Guardar imagen',
                    'name' :'grafico_ventas'
                }
            }
        },
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

#Filtro para todo el dashboard
def get_date_range(request):
    range_type = request.GET.get('range', None) 
    print('rango desde funcion get:date', range_type)
    
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

#Filtro para graficos individualmente
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

#Comparativa anual y mensual de grafico barras
def generar_comparativa_barras(df, tipo='anio'):
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
            'toolbox': {
                'show': True,
                'feature': {
                    'saveAsImage': {
                        'title': 'Guardar imagen',
                        'name' :'grafico_ventas'
                    }
                }
            },
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

        hoy = now().date()
        anio_actual = hoy.year
        mes_actual = hoy.month

        if mes_actual == 1:
            mes_anterior = 12
            anio_anterior = anio_actual - 1
        else:
            mes_anterior = mes_actual - 1
            anio_anterior = anio_actual

        meses_comparar = [
            (anio_anterior, mes_anterior),
            (anio_actual, mes_actual)
        ]

        # Crear etiquetas (labels) para los meses esperados, en orden
        etiquetas_esperadas = [
            f'{calendar.month_abbr[mes_anterior]} {anio_anterior}',
            f'{calendar.month_abbr[mes_actual]} {anio_actual}'
        ]

        agrupado['label'] = agrupado.apply(lambda r: f'{calendar.month_abbr[r["mes"]]} {r["anio"]}', axis=1)

        pivot = agrupado[
            agrupado[['anio', 'mes']].apply(tuple, axis=1).isin(meses_comparar)
        ].pivot_table(index='categoria', columns='label', values='valor', aggfunc='sum', fill_value=0)

        # Reindexar columnas para incluir siempre ambos meses
        pivot = pivot.reindex(columns=etiquetas_esperadas, fill_value=0).sort_index()

        dimensiones = ['Producto'] + etiquetas_esperadas

        source = []
        for categoria, fila in pivot.iterrows():
            fila_dict = {'Producto': categoria}
            for etiqueta, valor in fila.items():
                fila_dict[str(etiqueta)] = float(valor)
            source.append(fila_dict)

        option = {
            'legend': {},
            'toolbox': {
                'show': True,
                'feature': {
                    'saveAsImage': {
                        'title': 'Guardar imagen',
                        'name' :'grafico_ventas'
                    }
                }
            },
            'tooltip': {},
            'dataset': {
                'dimensions': dimensiones,
                'source': source
            },
            'xAxis': {'type': 'category'},
            'yAxis': {},
            'series': [{ 'type': 'bar' } for _ in dimensiones[1:]]
        }

        return option


    return {
        'tooltip': {'trigger': 'axis'},
        'legend': {'data': ['Sin datos']},
        'toolbox': {
            'show': True,
            'feature': {
                'saveAsImage': {
                    'title': 'Guardar imagen',
                    'name' :'grafico_ventas'
                }
            }
        },
        'xAxis': {'type': 'category', 'data': ['Sin datos'], 'name': 'Meses'},
        'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
        'series': [{'name': 'Sin datos', 'type': 'bar', 'data': [0]}]
    }

#Comparativa anual y mensual de grafico lineas
def generar_comparativa_lineas(df, tipo='anio'):
    if df.empty or 'anio' not in df.columns or 'mes' not in df.columns:
        return {
            'legend': {'data': ['Sin datos']},
            'tooltip': {'trigger': 'axis', 'showContent': True},
            'xAxis': {'type': 'category', 'data': ['Sin datos'], 'name': 'Meses' if tipo=='mes' else 'Años'},
            'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
            'series': [{'name': 'Sin datos', 'type': 'line', 'data': [0]}]
        }

    if tipo == 'anio':
        current_year = df['anio'].max()
        prev_year = current_year - 1
        años = [prev_year, current_year]

        pivot = df.pivot_table(
            index='categoria',
            columns='anio',
            values='valor',
            aggfunc='sum',
            fill_value=0
        )
        for y in años:
            if y not in pivot.columns:
                pivot[y] = 0
        pivot = pivot[años].sort_index()

        categorias = list(pivot.index)
        columnas = [str(y) for y in años]

        dataset_source = [['category'] + columnas]
        for cat in categorias:
            fila = [cat] + [float(pivot.at[cat, y]) for y in años]
            dataset_source.append(fila)

        chart = {
            'legend': {'data': categorias},
            'toolbox': {
                'show': True,
                'feature': {
                    'saveAsImage': {
                        'title': 'Guardar imagen',
                        'name' :'grafico_ventas'
                    }
                }
            },
            'tooltip': {'trigger': 'axis', 'showContent': True},
            'dataset': {'source': dataset_source},
            'xAxis': {'type': 'category', 'name': 'Años'},
            'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
            'series': [{
                'type': 'line',
                'smooth': True,
                'seriesLayoutBy': 'row',
                'emphasis': {'focus': 'series'}
            } for _ in categorias]
        }
        return chart

    elif tipo == 'mes':
        current_year = df['anio'].max()
        current_month = df[df['anio'] == current_year]['mes'].max()

        if current_month == 1:
            prev_month = 12
            prev_year = current_year - 1
        else:
            prev_month = current_month - 1
            prev_year = current_year

        meses_nombre = [
            f'{prev_year}-{calendar.month_name[prev_month].capitalize()}',
            f'{current_year}-{calendar.month_name[current_month].capitalize()}'
        ]

        df['anio_mes'] = list(zip(df['anio'], df['mes']))
        meses_comparar = [(prev_year, prev_month), (current_year, current_month)]

        pivot = df[df['anio_mes'].isin(meses_comparar)].pivot_table(
            index='categoria',
            columns='anio_mes',
            values='valor',
            aggfunc='sum',
            fill_value=0
        )
        for key in meses_comparar:
            if key not in pivot.columns:
                pivot[key] = 0
        pivot = pivot[meses_comparar].sort_index()

        categorias = list(pivot.index)
        columnas = [f'{k[0]}-{calendar.month_name[k[1]].capitalize()}' for k in meses_comparar]

        dataset_source = [['category'] + columnas]
        for cat in categorias:
            fila = [cat] + [float(pivot.at[cat, k]) for k in meses_comparar]
            dataset_source.append(fila)

        chart = {
            'legend': {'data': categorias},
            'toolbox': {
                'show': True,
                'feature': {
                    'saveAsImage': {
                        'title': 'Guardar imagen',
                        'name' :'grafico_ventas'
                    }
                }
            },
            'tooltip': {'trigger': 'axis', 'showContent': True},
            'dataset': {'source': dataset_source},
            'xAxis': {'type': 'category', 'name': 'Meses'},
            'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
            'series': [{
                'type': 'line',
                'smooth': True,
                'seriesLayoutBy': 'row',
                'emphasis': {'focus': 'series'}
            } for _ in categorias]
        }
        return chart

    else:
        return {
            'legend': {'data': ['Sin datos']},
            'toolbox': {
                'show': True,
                'feature': {
                    'saveAsImage': {
                        'title': 'Guardar imagen',
                        'name' :'grafico_ventas'
                    }
                }
            },
            'tooltip': {'trigger': 'axis', 'showContent': True},
            'xAxis': {'type': 'category', 'data': ['Sin datos'], 'name': 'Meses'},
            'yAxis': {'type': 'value', 'name': 'Ventas (Pesos)'},
            'series': [{'name': 'Sin datos', 'type': 'line', 'data': [0]}]
        }
