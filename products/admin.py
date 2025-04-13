from django.contrib import admin
from .models import Product, Category, Brand
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    fields = ('sku', 'name', 'price', 'brand', 'category', 'stock', 'description', 'main_image', 'secondary_image')
    list_display = ('__str__', 'slug', 'created_at')

admin.site.register(Product,ProductAdmin)
admin.site.register(Category)
admin.site.register(Brand)