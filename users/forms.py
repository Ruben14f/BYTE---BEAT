from django import forms

class Registro(forms.Form):
    username = forms.CharField(label='username',required=True, min_length=5, max_length=40, widget=forms.TextInput(attrs={
        'class':'form-control register-input',
        'placeholder': 'Nombres'
    }))
    lastname = forms.CharField(label='lastname',required=True, min_length=5, max_length=40, widget=forms.TextInput(attrs={
        'class':'form-control register-input',
        'placeholder': 'Apellidos'
    }))
    email = forms.EmailField(label='email',required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control  register-input',
        'placeholder':'correo@gmail.com'
    }))
    password = forms.CharField(label='password',required=True, widget=forms.PasswordInput(attrs={
        'class' : 'form-control  register-input',
        'placeholder' : 'Contraseña'
    }))
    
    password2 = forms.CharField(label='confirm password',required=True, widget=forms.PasswordInput(attrs={
        'class' : 'form-control  register-input',
        'placeholder' : 'Confirmar contraseña'
    }))