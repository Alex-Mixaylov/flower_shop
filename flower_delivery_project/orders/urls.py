from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shop', views.shop),
    path('product-details', views.product_details),
    path('thanks', views.thanks),
    path('contact', views.contact),
    path('collections', views.collections),
    path('cart', views.cart),
    path('checkout', views.checkout),
]