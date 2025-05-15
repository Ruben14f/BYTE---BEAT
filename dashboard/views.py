from django.shortcuts import render
from orden.models import Orden
import pandas as pd
import plotly.express as px 
from django.db.models import Sum


def dashboard_view(request):
    ordenes = Orden.objects.prefetch_related('productos_orden__producto').filter(fecha_pagada__isnull=False)

    data = []

    for orden in ordenes:
        for op in orden.productos_orden.all():
            data.append({
                'producto': op.producto.name,
                'cantidad': op.quantity,
                'fecha': orden.fecha_pagada.date() if orden.fecha_pagada else None,
            })

    if not data:
        return render(request, 'dashboard.html', {'grafico': 'No hay datos para mostrar'})

    df = pd.DataFrame(data)

    df_agrupado = df.groupby('producto')['cantidad'].sum().reset_index()
    
    

    fig = px.bar(df_agrupado, x='producto', y='cantidad', title='Productos más vendidos')
    
    fig.update_layout(
    dragmode=False,
    xaxis=dict(fixedrange=True),
    yaxis=dict(fixedrange=True)
    )
    config = {
    'scrollZoom': False,
    'displayModeBar': False,
    }
    grafico_html = fig.to_html(full_html=False,config=config)

    return render(request, 'dashboard_ordens.html', {'grafico': grafico_html})

