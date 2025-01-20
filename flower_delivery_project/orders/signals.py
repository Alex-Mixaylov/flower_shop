# signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem, Product
from django.db import transaction

@receiver(user_logged_in)
def merge_cart_on_login(sender, user, request, **kwargs):
    """
    При входе пользователя в систему, переносим корзину из сессии (гостя) в корзину пользователя.
    """
    session_cart = request.session.get('cart', {})
    if not session_cart:
        return  # Нет данных корзины в сессии

    try:
        # Получаем или создаем корзину пользователя
        user_cart, created = Cart.objects.get_or_create(user=user)

        with transaction.atomic():
            for product_id, item_data in session_cart.items():
                product = Product.objects.get(id=product_id)
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=user_cart,
                    product=product,
                    defaults={'quantity': item_data.get('quantity', 1)}
                )
                if not item_created:
                    # Если товар уже есть в корзине пользователя, увеличиваем количество
                    cart_item.quantity += item_data.get('quantity', 1)
                    cart_item.save()

        # Очистить корзину в сессии после переноса
        del request.session['cart']

    except Product.DoesNotExist:
        # Если товар из сессии не найден в базе данных, пропускаем его
        pass
    except Exception as e:
        # Логирование ошибки (опционально)
        print(f"Ошибка при переносе корзины: {e}")
