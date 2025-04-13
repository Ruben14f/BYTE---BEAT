from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
import uuid 

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)

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
    main_image = models.ImageField(upload_to='products/', blank=True)
    secondary_image = models.ImageField(upload_to='products/images/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=100, null=False,blank=False ,unique=True)


    def __str__(self):
        return self.name

def new_slug(sender, instance, *args, **kwargs):
     if instance.name and not instance.slug:
        slug = slugify(instance.name)
        
        while Product.objects.filter(slug=slug).exists():
            slug = slugify(
                '{}-{}'.format(instance.name, str(uuid.uuid4())[:8:])
            )
        instance.slug = slug
            
pre_save.connect(new_slug, sender=Product)