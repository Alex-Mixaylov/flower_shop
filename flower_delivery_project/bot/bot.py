import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramAPIError
from django.conf import settings
from dotenv import load_dotenv
import os

# Загрузка .env файла
load_dotenv()

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID")

# Логирование
logger = logging.getLogger('bot')

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

async def send_order_notification(order, event="created"):
    """
    Отправляет уведомление в Telegram о заказе.
    :param order: экземпляр модели Order
    :param event: событие ("created" или "status_changed")
    """
    try:
        # Формирование заголовка уведомления
        if event == "created":
            title = "🆕 Новый заказ!"
        elif event == "status_changed":
            title = "🔄 Обновление статуса заказа"
        else:
            title = "ℹ️ Уведомление о заказе"

        # Формирование текста сообщения
        message_text = (
            f"{title}\n"
            f"Заказ №{order.id}\n"
            f"Статус: {order.get_status_display()}\n"
            f"Имя получателя: {order.delivery.full_name}\n"
            f"Телефон: {order.customer_phone}\n"
            f"Адрес доставки: {order.delivery.address}\n\n"
            f"📦 Товары:\n"
        )

        # Добавление товаров в сообщение
        for item in order.items.all():
            message_text += (
                f"  - {item.product.name} — {item.quantity} шт., {item.total_price} руб.\n"
            )

        # Общая стоимость заказа
        message_text += f"\n💰 Общая стоимость: {order.total_price} руб."

        # Отправка основного сообщения
        await bot.send_message(chat_id=TELEGRAM_ADMIN_ID, text=message_text)

        # Отправка основного изображения товаров
        sent_images = set()  # Отслеживаем, чтобы не отправить одно изображение дважды
        for item in order.items.all():
            if item.product.image_main and item.product.image_main.url not in sent_images:
                await bot.send_photo(
                    chat_id=TELEGRAM_ADMIN_ID,
                    photo=item.product.image_main.url,
                    caption=f"{item.product.name}: {item.total_price} руб."
                )
                sent_images.add(item.product.image_main.url)  # Добавляем URL в множество

        logger.info(f"Уведомление для заказа {order.id} отправлено успешно.")

    except TelegramAPIError as e:
        logger.error(f"Ошибка Telegram API при отправке уведомления: {e}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")

# Функция для запуска бота (при необходимости)
async def run_bot():
    """
    Функция для запуска бота.
    """
    await dp.start_polling(bot)
