from django.urls import path
from . import views
from payment.views import crearTransaccion  

urlpatterns = [
    path('', views.orden, name='orden'),
    path('modificar_direccion/<int:orden_id>/', views.modificar_direccion, name='modificar_direccion'),
    path('add_address', views.add_new_address, name='add_address'),
    path('crear-transaccion/', crearTransaccion, name='crear_transaccion'),
    path('historial-pedidos/', views.historial_orden, name='historial_orden'),
    path('detalle-compra-realizada/<int:id>', views.detalle_compra, name='detalle_compra')
]
