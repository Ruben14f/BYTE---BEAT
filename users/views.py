from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth import authenticate, login as lg, logout as lgout
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
from .forms import Registro, RecuperarContraseñaForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings


# Create your views here.
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        usuarios = authenticate(request, username=username, password=password)
        
        if usuarios is not None:
            lg(request, usuarios)
            first_name = usuarios.first_name.capitalize()
            messages.success(request, f'Bienvenido {first_name}')

            if request.GET.get('next'):
                return HttpResponseRedirect(request.GET['next'])
            
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

    if request.method == 'POST' and form.is_valid():
        usuario = form.save()

        client_group = Group.objects.get(name='Clientes')
        usuario.groups.add(client_group)

        usuario.set_password(form.cleaned_data['password'])
        usuario.save()

        lg(request, usuario)
        firstname = usuario.first_name.capitalize()
        messages.success(request, f'Bienvenido {firstname}, tu registro ha sido exitoso.')
        return redirect('index') 

    return render(request, 'register.html' ,{
        'form' :form
    })

def password_reset(request):
    template_name = 'reset_password/password_reset.html'
    form = RecuperarContraseñaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        email = form.cleaned_data['email']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None
        
        if user:
            if not request.session.get('password_reset_sent', False):

                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                # Generar token y enviar el correo con el enlace de restablecimiento
                token = default_token_generator.make_token(user)
                reset_url = f'{settings.FRONTEND_DOMAIN}/recuperar-clave/{uidb64}/{token}'
                
                # request.build_absolute_uri(
                #     reverse_lazy('password_reset_confirm', kwargs={'uidb64': user.pk, 'token': token})
                # )

                html_message = f"""
                                    <html>
                                        <body>
                                            <p>Hola,</p>
                                            <p>Haz clic en el siguiente botón para restablecer tu contraseña:</p>
                                            <p>
                                                <a href="{reset_url}" style="display:inline-block;padding:10px 20px;background-color:#4CAF50;color:white;text-decoration:none;border-radius:5px;">
                                                    Restablecer contraseña
                                                </a>
                                            </p>
                                            <p>Si no solicitaste este cambio, puedes ignorar este mensaje.</p>
                                        </body>
                                    </html>
                                """
                send_mail(
                    'Restablece tu contraseña',
                    'Para restablecer tu contraseña, haz clic en el enlace',
                    # f'Para restablecer tu contraseña, haz clic en el siguiente enlace: {reset_url}',
                    'rmansilla.tech@gmail.com', 
                    [email],
                    fail_silently=False,
                    html_message= html_message
                )

                request.session['password_reset_sent'] = True
                messages.success(request, f'Correo enviado con exito, por favor revisa tu bandeja de entrada.')
            else:
                messages.error(request, 'Ya hemos enviado un correo para restablecer la contraseña. Por favor, revisa tu bandeja de entrada.')

        else:

            form.add_error('email', 'El correo no está registrado.')
    return render(request, template_name, {
        'form': form 
    })
    
def password_reset_confirm(request, uidb64, token):
    try:
        uid = uidb64 
        user = get_object_or_404(User, pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    validlink = False
    if user is not None and default_token_generator.check_token(user, token):
        validlink = True  

        if request.method == 'POST':
            form = SetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()  
                messages.success(request, f'Contraseña restablecida con exito')
                return redirect('login')
        else:
            form = SetPasswordForm(user=user) 

        return render(request, 'reset_password/password_reset_confirm.html', {'form': form, 'validlink': validlink})
    else:
        raise Http404("El enlace es inválido o ha expirado.")


