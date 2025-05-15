from django.urls import path
from .views import *

urlpatterns = [
    path('orden-list-report/', orden_list_report, name='orden_list_report'),
    path('orden-list-filter/', orden_list_filter, name='orden_list_filter'),
    # path('filter-status-report', estado_report_filter, name='buscar_estado_report'),
    # path('filter-fecha-report', fecha_filter_report, name='buscar_fecha_report'),
    path('descargar_ordenes/', orden_list_report, name='descargar_ordenes'),
    path('descargar-ordenes-filtradas/', orden_list_filter, name='descargar_ordenes_filtradas'),

]