from products.models import Product
from django import forms


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'sku',
            'name', 
            'price',
            'brand',
            'category',
            'stock',
            'description',
            'main_image',
            'secondary_image']
        
        labels = { 
            'brand': 'Marca', 
            'category': 'Categoria',
            'name' : 'Nombre',
            'price': 'Precio',
            'stock' : 'Cantidad',
            'description' : 'Descripcion',
            'main_image' : 'Imagen principal',
            'secondary_image' : 'Imagen secundaria'}

        widgets = {
            'sku': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'name': forms.TextInput(attrs={'class': 'form-control mb-3'}),
            'price': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'brand': forms.Select(attrs={'class': 'form-select mb-3'}),
            'category': forms.Select(attrs={'class': 'form-select mb-3'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control mb-3'}),
            'description': forms.Textarea(attrs={'class': 'form-control mb-3'}),
            'main_image': forms.FileInput(attrs={'class': 'form-control mb-3', 'accept' : 'image/*'}),
            'secondary_image': forms.FileInput(attrs={'class': 'form-control mb-3' , 'accept' : 'image/*'}),
        }
        