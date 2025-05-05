from django.urls import path
from . views import *

urlpatterns = [
    path('', index, name='index'),
    path('admin-index',index_admin, name='index_admin')
]
