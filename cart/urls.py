from django.urls import path
from . views import *


urlpatterns = [
    path('cart/', cart, name='cart'),
    path('addCart/', addCart, name='add'),
    path('remove/', remove, name='remove')

]
