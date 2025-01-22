# bot.py

import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.exceptions import TelegramAPIError
from dotenv import load_dotenv
import os
import threading

# Загрузка переменных окружения из .env файла
load_dotenv()

# Конфигурация
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID")

# Настройка логирования
logger = logging.getLogger('bot')
logger.setLevel(logging.DEBUG)  # Уровень логирования

# Создание консольного обработчика логов
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Создание форматтера и добавление его к обработчику
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(console_handler)

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

# Создание нового event loop для бота
loop = asyncio.new_event_loop()

def start_bot():
    """
    Запуск бота в отдельном потоке с его собственным event loop.
    """
    global loop
    asyncio.set_event_loop(loop)
    try:
        logger.info("Запуск Telegram бота...")
        loop.run_until_complete(dp.start_polling(bot))
    except Exception as e:
        logger.error(f"Ошибка при запуске Telegram бота: {e}")

# Запуск бота в отдельном потоке
bot_thread = threading.Thread(target=start_bot, daemon=True)
bot_thread.start()
logger.info("Поток Telegram бота запущен.")

async def send_order_notification_async(order, event="created"):
    """
    Асинхронная функция для отправки уведомления о заказе в Telegram.
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
            f"📦 Букеты:\n"
        )

        # Добавление товаров в сообщение
        for item in order.items.all():
            message_text += (
                f"  - {item.product.name} — {item.quantity} шт., {item.total_price} $.\n"
            )

        # Общая стоимость заказа
        message_text += f"\n💰 Total cost: {order.total_price} $."

        # Отправка основного сообщения
        await bot.send_message(chat_id=TELEGRAM_ADMIN_ID, text=message_text)

        # Отправка основного изображения товаров
        sent_images = set()  # Отслеживание уже отправленных изображений, чтобы избежать дубликатов
        for item in order.items.all():
            if item.product.image_main and item.product.image_main.url not in sent_images:
                await bot.send_photo(
                    chat_id=TELEGRAM_ADMIN_ID,
                    photo=item.product.image_main.url,
                    caption=f"{item.product.name}: {item.total_price} $."
                )
                sent_images.add(item.product.image_main.url)  # Добавляем URL в множество

        logger.info(f"Уведомление для заказа {order.id} отправлено успешно.")

    except TelegramAPIError as e:
        logger.error(f"Ошибка Telegram API при отправке уведомления: {e}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")

def send_order_notification(order, event="created"):
    """
    Синхронная функция для планирования отправки уведомления о заказе в Telegram.
    :param order: экземпляр модели Order
    :param event: событие ("created" или "status_changed")
    """
    try:
        # Планирование асинхронной функции на event loop бота
        asyncio.run_coroutine_threadsafe(
            send_order_notification_async(order, event),
            loop
        )
        logger.debug(f"Уведомление для заказа {order.id} запланировано.")
    except Exception as e:
        logger.error(f"Ошибка при планировании уведомления для заказа {order.id}: {e}")
