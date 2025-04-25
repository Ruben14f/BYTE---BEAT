from django.urls import path
from . import views

urlpatterns = [
    path('', views.orden, name='orden'),
    path('modificar_direccion/<int:orden_id>/', views.modificar_direccion, name='modificar_direccion'),
]
