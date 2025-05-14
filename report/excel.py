import pandas as pd
from pandas import ExcelWriter
import os
from orden.models import Orden



# def export_excel():
#     ruta = r'C:\Users\ruben.mansilla\Desktop\BYTE---BEAT\reporte_excel'

#     datos = pd.DataFrame({
#         'id' : [1,2,3,4],
#         'nombre' : ['ruben', 'maria', 'jose', 'pablo'],
#         'apellido' : ['mansilla', 'perez', 'gonzalez', 'pinto'],
#     })

#     datos = datos[['id', 'nombre', 'apellido']]

#     writer = ExcelWriter(ruta +"/reporte.xlsx" , engine='xlsxwriter')

#     datos.to_excel(writer, sheet_name='reporte', index=False)

#     writer.close()

def ordens():
    ordenes = Orden.objects.all()
    print(ordenes) 
