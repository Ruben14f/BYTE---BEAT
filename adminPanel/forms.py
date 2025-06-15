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
            'secondary_image'
        ]
        
        labels = { 
            'sku': 'SKU',
            'name': 'Nombre',
            'price': 'Precio',
            'brand': 'Marca', 
            'category': 'Categoría',
            'stock': 'Cantidad',
            'description': 'Descripción',
            'main_image': 'Imagen principal',
            'secondary_image': 'Imagen secundaria'
        }

        widgets = {
            'sku': forms.TextInput(attrs={
                'class': 'form-control w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-50 text-gray-500',
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all input-focus',
                'placeholder': 'Ingresa el nombre del producto'
            }),
            'price': forms.NumberInput(attrs={
                'class': 'form-control w-full pl-8 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all input-focus',
                'min': '0',
                'step': '1',  
            }),
            'brand': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all input-focus'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all input-focus'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all input-focus',
                'min': '0',
                'placeholder': '0'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all input-focus resize-none',
                'rows': 4,
                'placeholder': 'Describe las características del producto...'
            }),
            'main_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'secondary_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        # Verifica si el objeto está siendo editado
        edit_mode = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)
        
        # Si es un formulario de edición, hacer el SKU no editable
        if edit_mode:
            self.fields['sku'].widget.attrs['readonly'] = True
            self.fields['sku'].widget.attrs['class'] = 'form-control w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all input-focus'
    
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('El precio no puede ser menor a 0')
        return price
    
    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('La cantidad no puede ser menor a 0')
        return stock