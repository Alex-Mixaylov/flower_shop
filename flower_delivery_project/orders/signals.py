# signals.py

from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartItem, Product
from django.db import transaction

from django.db.models.signals import post_save
from orders.models import Order
from bot.bot import send_order_notification


import asyncio
from asgiref.sync import sync_to_async

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

# Настройка логирования
logger = logging.getLogger('orders')

@receiver(post_save, sender=Order)
def notify_telegram_on_order_save(sender, instance, created, **kwargs):
    """
    Отправляет уведомление в Telegram при создании нового заказа или изменении его статуса.
    Использует transaction.on_commit для гарантии, что все связанные объекты сохранены.
    """
    try:
        if created:
            logger.info(f"New order has created: {instance.id}")
            event = "created"
        else:
            logger.info(f"Order status has changed {instance.id} to {instance.status}")
            event = "status_changed"

        # Используем transaction.on_commit для отправки уведомления после сохранения транзакции
        def send_notification():
            try:
                # Перезагружаем экземпляр из базы данных, чтобы гарантировать наличие delivery
                order = Order.objects.select_related('delivery').prefetch_related('items__product').get(id=instance.id)

                if not hasattr(order, 'delivery') or order.delivery is None:
                    logger.error(f"Order {order.id} has no delivery.")
                    return  # Прерываем выполнение, если нет delivery

                # Извлечение необходимых данных из заказа
                order_data = {
                    'id': order.id,
                    'status': order.get_status_display(),
                    'full_name': order.delivery.full_name,
                    'customer_phone': order.customer_phone,
                    'address': order.delivery.address,
                    'items': list(order.items.all()),  # Список элементов заказа
                    'total_price': order.total_price,
                }

                # Отправка уведомления
                send_order_notification(order_data, event=event)
            except Order.DoesNotExist:
                logger.error(f"Order with id {instance.id} does not exist.")
            except Exception as e:
                logger.error(f"Error while senging new order status update message {instance.id}: {e}")

        transaction.on_commit(send_notification)
        logger.debug(f"Message for Order {instance.id} is planned after commit.")
    except Exception as e:
        logger.error(f"Error of send_order_notification: {e}")