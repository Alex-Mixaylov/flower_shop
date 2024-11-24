from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('product-details/', views.product_details, name='product_details'),
    path('thanks/', views.thanks, name='thanks'),
    path('contact/', views.contact, name='contact'),
    path('collections/', views.collections, name='collections'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout')
]