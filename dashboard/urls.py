from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard_admin'),
    path('api/get-chart2/', get_chart2, name='get_chart2'),
    path('api/get-chart3/', get_chart3, name='get_chart3'),
    path('api/get-chart4/', get_chart4, name='get_chart4'),

]