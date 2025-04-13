from django.urls import path
from . import views



urlpatterns = [
    path('productsList/', views.ProductListView.as_view(), name='view_products'),
    path('productDetail/<slug:slug>', views.ProductListView.as_view(), name='detail_product'),
]