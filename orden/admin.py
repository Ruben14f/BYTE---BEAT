from django.contrib import admin
from .models import Orden, OrderAddress,OrdenProducto
# Register your models here.
admin.site.register(Orden)
admin.site.register(OrderAddress)
admin.site.register(OrdenProducto)
