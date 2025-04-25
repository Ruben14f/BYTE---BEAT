from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Address
from orden.models import OrderAddress

class OrderAddressForm(forms.ModelForm):
    class Meta:
        model = OrderAddress
        fields = ['calle', 'num_direccion', 'comuna', 'ciudad']

    calle = forms.CharField(label='Calle',
        widget=forms.TextInput(attrs={  
            'placeholder': 'Nombre calle'
        }),
        required=True
    )

    num_direccion = forms.CharField(label='Numero de calle',
        widget=forms.TextInput(attrs={  
            'placeholder': 'Numero de calle'
        }),
        required=True
    )

    def clean_num_direccion(self):
        num_direccion = self.cleaned_data.get('num_direccion')
        if not num_direccion.isdigit(): 
            raise forms.ValidationError("El número de calle debe ser solo numérico.")
        return num_direccion
    
class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['calle', 'num_direccion', 'comuna', 'ciudad']

    calle = forms.CharField(label='Calle',
        widget=forms.TextInput(attrs={  
            'placeholder': 'Nombre calle'
        }),
        required=True
    )

    num_direccion = forms.CharField(label='Numero de calle',
        widget=forms.TextInput(attrs={  
            'placeholder': 'Numero de calle'
        }),
        required=True
    )

    def clean_num_direccion(self):
        num_direccion = self.cleaned_data.get('num_direccion')
        if not num_direccion.isdigit(): 
            raise forms.ValidationError("El número de calle debe ser solo numérico.")
        return num_direccion

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number']
        
    phone_number = forms.CharField(label='Telefono',
        widget=forms.TextInput(attrs={  
            'placeholder': 'Número de teléfono'
        }),
        required=True
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit(): 
            raise forms.ValidationError("El número de teléfono debe ser solo numérico.")
        return phone_number

class UserForm(forms.ModelForm):
    first_name = forms.CharField(label='Nombres', max_length=100)
    last_name = forms.CharField(label='Apellidos', max_length=100)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

    
class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(label='Contraseña actual', widget=forms.PasswordInput(), required=True)
    new_password = forms.CharField(label='Nueva Contraseña', widget=forms.PasswordInput(), required=False)
    confirm_password = forms.CharField(label='Confirmar Nueva Contraseña', widget=forms.PasswordInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        current_password = cleaned_data.get('current_password')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        user = self.user 

        if current_password and not user.check_password(current_password):
            self.add_error('current_password', 'La contraseña actual es incorrecta')

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', 'Las contraseñas no coinciden')

        return cleaned_data