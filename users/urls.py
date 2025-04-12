from django.urls import path
from . views import *



urlpatterns = [
    path('login/',login, name='login'),
    path('logout/',logout_view, name='logout'),
    path('register/', register, name='register'),
    path('reset_password/', password_reset, name='password_reset'),
    path('reset_password/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),

]