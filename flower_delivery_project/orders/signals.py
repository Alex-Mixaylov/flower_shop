# signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem, Product
from django.db import transaction
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from orders.models import Order
from bot.bot import send_order_notification

# Настройка логирования
import logging
logger = logging.getLogger('orders')


@receiver(user_logged_in)
def merge_cart_on_login(sender, user, request, **kwargs):
    """
    При входе пользователя в систему, переносим корзину из сессии (гостя) в корзину пользователя.
    """
    logger.debug(f"User {user.username} logged in. Attempting to merge session cart into user cart.")
    session_cart = request.session.get('cart', {})
    logger.debug(f"Session cart before merge: {session_cart}")

    if not session_cart:
        logger.debug("No session cart data to merge.")
        return  # Нет данных корзины в сессии

    try:
        # Получаем или создаем корзину пользователя
        user_cart, created = Cart.objects.get_or_create(user=user)
        logger.debug(f"User cart {'created' if created else 'retrieved'}: Cart ID {user_cart.id}")

        with transaction.atomic():
            for product_id, item_data in session_cart.items():
                try:
                    product = Product.objects.get(id=product_id)
                    cart_item, item_created = CartItem.objects.get_or_create(
                        cart=user_cart,
                        product=product,
                        defaults={'quantity': item_data.get('quantity', 1)}
                    )
                    if not item_created:
                        # Если товар уже есть в корзине пользователя, увеличиваем количество
                        old_quantity = cart_item.quantity
                        cart_item.quantity += item_data.get('quantity', 1)
                        cart_item.save()
                        logger.debug(
                            f"Updated CartItem: {product.name} quantity from {old_quantity} to {cart_item.quantity}.")
                    else:
                        logger.debug(f"Added new CartItem: {product.name} with quantity {cart_item.quantity}.")
                except Product.DoesNotExist:
                    logger.error(f"Product with ID {product_id} does not exist. Skipping.")

        # Очистить корзину в сессии после переноса
        del request.session['cart']
        logger.debug("Session cart data cleared after merging.")

    except Exception as e:
        # Логирование ошибки
        logger.error(f"Error merging cart: {e}")

#Telegram bot

@receiver(post_save, sender=Order)
def notify_telegram_on_order_save(sender, instance, created, **kwargs):
    """
    Отправляет уведомление в Telegram при создании нового заказа или изменении его статуса.
    """
    try:
        # Если заказ новый
        if created:
            logger.info(f"Новый заказ создан: {instance.id}")
            send_order_notification(instance, event="created")
        else:
            # Если изменился статус заказа
            logger.info(f"Изменен статус заказа {instance.id} на {instance.status}")
            send_order_notification(instance, event="status_changed")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления для заказа {instance.id}: {e}")
