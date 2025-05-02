from django.urls import path
from . views import *



urlpatterns = [
    path("", webpay_respuesta, name="webpay_respuesta"),

]