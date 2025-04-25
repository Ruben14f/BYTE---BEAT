from django.db import models
from users.models import User
from products.models import Product
import uuid
from django.db.models.signals import pre_save , m2m_changed,post_save



# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=100, null=False, blank=False, unique=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    productos = models.ManyToManyField(Product, through='CartProduct')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2,  default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
    def update_totals(self):
        self.update_subtotal()
        self.update_total()

        if self.orden:
            self.orden.update_total()
    
    
    def update_subtotal(self):
        self.subtotal = sum([i.quantity * i.productos.price for i in self.product_related()])
        self.save()
    
    def update_total(self):
        self.total = self.subtotal
        self.save()

    def product_related(self):
        return self.cartproduct_set.select_related('productos')
    @property
    def orden (self):
        return self.orden_set.first()
    
class CartProductManager(models.Manager):

    def crearActualizar(self, cart, productos, quantity=1):
        object, created = self.get_or_create(cart=cart, productos=productos)

        if not created:
            quantity = object.quantity + quantity
            object.save()

        object.update_quantity(quantity)
        return object


class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    productos = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


    objects = CartProductManager()

    def update_quantity(self, quantity):
        self.quantity = quantity
        self.save()
        
    def __str__(self):
        return f"{self.cart.cart_id} - {self.productos.name}"
    


def set_cart_id(sender, instance, *args, **kwargs):
    if not instance.cart_id:
        instance.cart_id = str(uuid.uuid4())

def update_totals(sender, instance, action, *args, **kwargs):
    if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
        instance.update_totals()

def postActualizar(sender, instance, *args, **kwargs):
    instance.cart.update_totals()

post_save.connect(postActualizar, sender=CartProduct)
pre_save.connect(set_cart_id, sender=Cart)
m2m_changed.connect(update_totals, sender=Cart.productos.through)

