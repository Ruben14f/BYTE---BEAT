from django.urls import path
from .views import inicio_bot, menu_bot_view

urlpatterns = [
    path('menu/', menu_bot_view, name='menu_bot_view'),
    path('bot/', inicio_bot, name='inicio'),
    
]