from django.urls import path
from .views import *

urlpatterns = [
    path('dashboard/', dashboard_view, name='dashboard'),
    path('api/get-chart/', get_chart, name='get_chart'),
]