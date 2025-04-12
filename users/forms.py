from django import forms
from django.contrib.auth.models import User


class Registro(forms.Form):

    firstname = forms.CharField(label='Nombres',required=True, min_length=5, max_length=40, widget=forms.TextInput(attrs={
        'class':'form-control register-input',
        'placeholder': 'Nombres'
    }))
    lastname = forms.CharField(label='Apellidos',required=True, min_length=5, max_length=40, widget=forms.TextInput(attrs={
        'class':'form-control register-input',
        'placeholder': 'Apellidos'
    }))
    email = forms.EmailField(label='Correo',required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control  register-input',
        'placeholder':'correo@gmail.com'
    }))
    password = forms.CharField(label='Contraseña',required=True, widget=forms.PasswordInput(attrs={
        'class' : 'form-control  register-input',
        'placeholder' : 'Contraseña'
    }))
    
    password2 = forms.CharField(label='Confirmar contraseña',required=True, widget=forms.PasswordInput(attrs={
        'class' : 'form-control  register-input',
        'placeholder' : 'Confirmar contraseña'
    }))

#self para poder acceder a los atributos de username
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Correo ya registrado, intente con otro')
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password2') != cleaned_data.get('password'):
            self.add_error('password2', 'La contraseña no coicide')
        
    def save(self):
        usuario = User.objects.create_user(
            username=self.cleaned_data.get('email'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('password')
        )
    
        usuario.first_name = self.cleaned_data.get('firstname')
        usuario.last_name = self.cleaned_data.get('lastname')

        usuario.save()
        return usuario
    
class RecuperarContraseñaForm(forms.Form):
    email = forms.EmailField(
        label='Correo Electrónico', 
        required=True, 
        widget=forms.EmailInput(attrs={
            'class': 'form-control login-input',
            'placeholder': 'correo@ejemplo.com'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('El correo no está registrado')
        return email