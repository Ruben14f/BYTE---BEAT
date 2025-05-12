from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
import uuid
from cloudinary.models import CloudinaryField
from cloudinary.uploader import upload

class ProductStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Activo'
    INACTIVE = 'INACTIVE', 'Agotado'

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Product(models.Model):
    sku = models.CharField(max_length=20, unique=True, null=False, blank=False)
    name = models.CharField(max_length=100, null=False, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    stock = models.IntegerField(null=False, blank=False)
    description = models.TextField(null=False, blank=True)
    main_image = CloudinaryField('image', blank=True)
    secondary_image = CloudinaryField('image', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=100, null=False, blank=False, unique=True)
    status = models.CharField(max_length=40, choices=ProductStatus.choices, default=ProductStatus.ACTIVE)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.pk:
            original = Product.objects.get(pk=self.pk)
            self.__original_main_image = original.main_image
            self.__original_secondary_image = original.secondary_image
        else:
            self.__original_main_image = self.main_image
            self.__original_secondary_image = self.secondary_image

        super(Product, self).save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.status = ProductStatus.INACTIVE 
        else:
            self.status = ProductStatus.ACTIVE  
        super().save(*args, **kwargs)

def new_slug(sender, instance, *args, **kwargs):
    if instance.name and not instance.slug:
        slug = slugify(instance.name)

        while Product.objects.filter(slug=slug).exists():
            slug = slugify('{}-{}'.format(instance.name, str(uuid.uuid4())[:8:]))
        instance.slug = slug

def optimize_image(sender, instance, **kwargs):
    if hasattr(instance, '__original_main_image') and instance.main_image and (instance.main_image != instance.__original_main_image):
        uploaded_image = upload(instance.main_image, transformation=[{
            'quality': '70', 'fetch_format': 'auto'
        }], folder='products')
        

        instance.main_image = uploaded_image['secure_url']  


    if hasattr(instance, '__original_secondary_image') and instance.secondary_image and (instance.secondary_image != instance.__original_secondary_image):
        uploaded_image = upload(instance.secondary_image, transformation=[{
            'quality': '70', 'fetch_format': 'auto'
        }], folder='products')

        instance.secondary_image = uploaded_image['secure_url']

pre_save.connect(new_slug, sender=Product)
pre_save.connect(optimize_image, sender=Product)
