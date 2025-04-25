from django.urls import path
from . views import *



urlpatterns = [
    path('', Profile, name='perfil'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('change_password/', change_password, name='change_password'),

]