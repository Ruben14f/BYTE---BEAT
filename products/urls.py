from django.urls import path
from . import views

urlpatterns = [
    path('productsList/', views.ProductListView.as_view(), name='view_products'),
    path('search/', views.ProductSearchListView.as_view(), name='search_product'),
    path('productDetail/<slug:slug>', views.ProductDateilView.as_view(), name='detail_product'),
]
