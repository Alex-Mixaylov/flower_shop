from django.contrib import admin
from .models import User, Collection, Bouquet, Order, OrderItem, ContactMessage

# Регистрация моделей в админке
admin.site.register(User)
admin.site.register(Collection)
admin.site.register(Bouquet)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ContactMessage)
