from django.urls import path
from . views import *


urlpatterns = [
    path('cart/', cart, name='cart'),
    path('addCart/', addCart, name='add'),
    path('remove/', remove, name='remove'),
    path('update-cart-product/', update_cart_product, name='update_cart_product'),

]
