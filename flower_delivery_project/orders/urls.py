from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('product-details/', views.product_details, name='product_details'),
    path('thanks/', views.thanks, name='thanks'),
    path('contact/', views.contact, name='contact'),
    path('collections/', views.collections, name='collections'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('about/', views.about, name='about')
]

# Подключение статических файлов в режиме разработки
if settings.DEBUG:  # Эта строка важна, чтобы не использовать static() в production
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)