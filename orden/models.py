from django.db import models
from users.models import User
from cart.models import Cart
from profiles.models import Comuna, Ciudad
from django.db.models.signals import pre_save
import uuid

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    status = models.CharField(max_length=40, choices=OrdenStatus.choices, default=OrdenStatus.CREATED)
    delivery_method = models.CharField(max_length=40, choices=DeliveryMethod.choices, default=DeliveryMethod.SHIPPING)
    envio_total = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    total = models.DecimalField(default=0, max_digits=9, decimal_places=2)
    create_at = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return self.ordenID
    
    def get_total(self):
        return self.cart.total + self.envio_total
    
    def update_total(self):
        self.total = self.get_total()
        self.save()

    def save(self, *args, **kwargs):
        if not self.delivery_method:
            self.delivery_method = DeliveryMethod.SHIPPING 
        
        if self.delivery_method == DeliveryMethod.SHIPPING:
            self.envio_total = 3990  
        else:
            self.envio_total = 0  

        self.total = self.cart.subtotal + self.envio_total
        super().save(*args, **kwargs) 


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
    instance.total = instance.get_total()

pre_save.connect(enviarOrden, sender=Orden)
pre_save.connect(enviar_total, sender=Orden)