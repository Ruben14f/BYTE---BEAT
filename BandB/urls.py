"""
URL configuration for BandB project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

# Vista personalizada para redirigir a /admin solo si es admin
@login_required
def admin_access(request):
    if not request.user.is_superuser:  # Si no es admin (superusuario)
        return HttpResponseRedirect('/')  # Redirigir al inicio si no es admin

    # Si el usuario es admin, redirigir al panel de administración de Django
    return HttpResponseRedirect('/django-admin/')  # Redirige correctamente al panel de administración de Django

# Asegúrate de que el acceso al admin esté restringido correctamente
@login_required
def django_admin_access(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')  # Redirigir al inicio si no es admin
    
    # Si es admin, continuar con la vista normal del admin
    return admin.site.admin_view(admin.site.index)(request)

urlpatterns = [
    # Usa la vista personalizada aquí
    path('admin/', admin_access),  # Protege la vista de admin con login_required

    # Asegúrate de incluir el panel de administración de Django en tu urlpatterns
    path('django-admin/', admin.site.urls, name="admin-django"),  
    path('', include('core.urls')),
    path('usuario/', include('users.urls')),
    path('productos/', include('products.urls')),
    path('carrito/', include('cart.urls')),
    path('orden/', include('orden.urls')),
    path('perfil/', include('profiles.urls')),
    path('webpay/', include('payment.urls')),
    path('admin-view/', include('adminPanel.urls')),
    path('admin-report/', include('report.urls')),
    path('admin-dashboard/', include('dashboard.urls')),
    path('chatbot/', include('chatbot_web.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

    