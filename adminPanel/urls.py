from django.urls import path
from .views import  *


urlpatterns = [
    path('agregar-product', agregar_producto, name='agregar_product'),
    path('list-product', listado_productos, name='list_product_admin'),
    path('modificar-product/<int:id>', modificar_producto, name='editar_product_admin'),
    path('eliminar-product/<int:id>', eliminar_producto, name='eliminar_product_admin'),
    path('list-ordenes', listado_ordenes, name="list_ordenes_admin"),
    path('filter-orden', orden_search, name='buscar_orden'),
    path('filter-status', estado_search, name='buscar_estado'),
    
]