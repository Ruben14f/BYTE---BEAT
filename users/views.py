from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login as lg, logout as lgout
from django.contrib import messages
from .forms import Registro

# Create your views here.
def login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuarios = authenticate(request, username=username, password=password)

        if usuarios:
            lg(request, usuarios)
            messages.success(request, f'Bienvenido {username}')
            return redirect('index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
            return render(request, 'login.html', {'intento': True})
       
    return render(request, 'login.html', {'intento': False})

def logout_view(request):
    lgout(request)
    messages.info(request, 'Has cerrado sesión correctamente. Esperamos verte pronto! ')
    return redirect('index')

def register(request):
    form = Registro(request.POST or None)
    if form.is_valid(): 

        messages.success(request, f'Bienvenido, tu registro ha sido exitoso.')
        return redirect('index') 

    return render(request, 'register.html' ,{
        'form' :form
    })