from django.urls import path
from .views import  *


urlpatterns = [
    path('agregar-product', agregar_producto, name='agregar_product'),
    path('list-product', listado_productos, name='list_product_admin'),
    path('modificar-product/<int:id>', modificar_producto, name='editar_product_admin'),
    path('eliminar-product/<int:id>', eliminar_producto, name='eliminar_product_admin'),
    path('detail-product-admin/<int:id>', detail_product, name='detail_product_admin'),
    path('filter-sku', sku_search, name='buscar_sku'),
    path('filter-marca', marca_search, name='buscar_marca'),
    path('filter-categoria', categoria_search, name='buscar_categoria'),
    path('filter-status-product', estado_product_search, name='buscar_estado_producto'),
    path('list-ordenes', listado_ordenes, name="list_ordenes_admin"),
    path('filter-orden', orden_search, name='buscar_orden'),
    path('filter-status', estado_search, name='buscar_estado'),
    path('detail-orden-admin/<int:id>', detail_orden, name='detail_orden_admin'),
    path('update-status-orden/<int:id>', update_status_orden, name='actualizar_estado_orden'),
    

]