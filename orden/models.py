from datetime import datetime
from django.db import models 
from django.db.models import  Max, Sum,F
from users.models import User
from cart.models import Cart
from products.models import Product
from profiles.models import Comuna, Ciudad
from django.db.models.signals import pre_save
import uuid
from django.db.models.functions import Coalesce
from django.utils.timezone import localdate

class OrdenStatus(models.TextChoices):
    CREATED = 'CREATED', 'Creado'
    PAYED = 'PAYED', 'Pagado'
    PREPARING = 'PREPARING', 'Preparando'
    SHIPPED = 'SHIPPED', 'Enviado'
    READY_FOR_PICKUP = 'READY_FOR_PICKUP', 'Listo para retirar'
    DELIVERED = 'DELIVERED', 'Entregado'
    CANCELED = 'CANCELED', 'Cancelado'

class DeliveryMethod(models.TextChoices):
    SHIPPING = 'SHIPPING', 'Envío'
    PICKUP = 'PICKUP', 'Retiro'

# Create your models here.
class Orden(models.Model):
    ordenID = models.CharField(max_length=100, null=False, blank=False, unique=True)
    num_orden = models.PositiveIntegerField(unique=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=40, choices=OrdenStatus.choices, default=OrdenStatus.CREATED)
    delivery_method = models.CharField(max_length=40, choices=DeliveryMethod.choices, default=DeliveryMethod.SHIPPING)
    envio_total = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    total = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    create_at = models.DateField(auto_now_add=True)
    token_ws = models.CharField(max_length=255, blank=True, null=True)
    fecha_pagada = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.ordenID
    
    def get_total(self):
        return self.cart.subtotal + self.envio_total
    
    def update_total(self):
        self.total = self.get_total()
        self.save()

    @classmethod
    def ordenes_recentes(cls, limite=10):
        hoy = localdate() 
        return (
            cls.objects
            .filter(create_at=hoy, status='PAYED')  
            .annotate(total_vendido=Coalesce(Sum('productos_orden__quantity'), 0))  
            .order_by('-fecha_pagada') 
            [:limite] 
        )
    

class OrdenProducto(models.Model):
    orden = models.ForeignKey('Orden', on_delete=models.CASCADE, related_name='productos_orden')
    producto = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    @classmethod
    def total_productos_mas_vendido(cls,limite=5):
        current_year = datetime.now().year
        return (
            Product.objects
            .annotate(total_vendido=Sum('ordenproducto__quantity'),
                      total_vendido_precio=Sum(F('ordenproducto__quantity') * F('price')))
            .filter(total_vendido__gt=0,
                    ordenproducto__orden__status='DELIVERED',
                    ordenproducto__orden__fecha_pagada__year=current_year)
            .order_by('-total_vendido')[:limite]
        )
    
    @classmethod
    def product_recomendate(cls):
        return (
            Product.objects
            .annotate(total_vendido=Coalesce(Sum('ordenproducto__quantity'), 0))
            .order_by('-total_vendido') 
        )
    

    def __str__(self):
        return f"{self.producto.name} x{self.quantity} (Orden {self.orden.ordenID})"


class OrderAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey('Orden', on_delete=models.CASCADE)
    calle = models.CharField(max_length=225, blank=False, null=True)
    num_direccion = models.IntegerField(blank=False, null=False)
    comuna = models.ForeignKey(Comuna, on_delete=models.CASCADE, blank=False, null=False)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, blank=False, null=False)

    def __str__(self):
        return f"Dirección de pedido {self.order.id} - {self.calle}, {self.num_direccion}, {self.ciudad}, {self.comuna.name}"

    def full_address(self):
        return f"{self.direccion}, {self.ciudad}, {self.comuna.name}"
    

def enviarOrden(sender, instance, *args, **kwargs):
    if not instance.ordenID:
        instance.ordenID = str(uuid.uuid4())

def enviar_total(sender, instance, *args, **kwargs):
    if instance._state.adding:
        instance.total = instance.get_total()


def asig_num_oren(sender, instance, *args, **kwargs):
    if instance.num_orden is None:
        #buscar el numero mas alto en la base de datos
        last = Orden.objects.aggregate(max_num=Max('num_orden'))['max_num']
        if last is not None:
            instance.num_orden = last + 10
        else:
            instance.num_orden = 1010

pre_save.connect(asig_num_oren, sender=Orden)
pre_save.connect(enviarOrden, sender=Orden)
pre_save.connect(enviar_total, sender=Orden)