from . import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('shop/', views.shop, name='shop'),
    path('product/<slug:slug>/', views.product_details, name='product_details'),
    path('thanks/', views.thanks, name='thanks'),
    path('contact/', views.contact, name='contact'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('about/', views.about, name='about'),
    path('collections/', views.collections, name='collections'),
    path('collections/<slug:slug>/', views.collection_detail, name='collection_detail'),
    path('personal-cabinet/', views.personal_cabinet, name='personal_cabinet'),
    # Маршруты для коллекций и категорий в footer
    path('collection/<slug:slug>/', views.shop_by_collection, name='shop_by_collection'),
    path('category/<slug:slug>/', views.shop_by_category, name='shop_by_category'),
    # Маршрут для AJAX изменения кол-ва товара в Корзине
    path('update-cart-quantity/', views.update_cart_quantity, name='update_cart_quantity'),
    # Маршрут для переключения "Избранных" AJAX
    path('favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),

]

# Подключение статических файлов в режиме разработки
if settings.DEBUG:  # Эта строка важна, чтобы не использовать static() в production
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)