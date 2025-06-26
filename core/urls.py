from django.urls import path
from . views import *

urlpatterns = [
    path('', index, name='index'),
    path('admin-index',index_admin, name='admin_index'),
    path('tests-design',tests, name='tests'),
    path('formulario-contacto',form_contacto, name='formulario_contacto'),


]
