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

# Проверка наличия необходимых переменных окружения
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("Необходимо задать TELEGRAM_BOT_TOKEN в переменных окружения.")
if not TELEGRAM_ADMIN_ID:
    raise ValueError("Необходимо задать TELEGRAM_ADMIN_ID в переменных окружения.")

# Настройка логирования
logger = logging.getLogger('bot')
logger.setLevel(logging.DEBUG)  # Уровень логирования

# Создание пользовательского обработчика логов для предотвращения ошибок кодировки
class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            msg = self.format(record)
            self.stream.write(msg + self.terminator)
            self.flush()
        except UnicodeEncodeError:
            # Замена неподдерживаемых символов
            msg = msg.encode('utf-8', errors='replace').decode('utf-8')
            self.stream.write(msg + self.terminator)
            self.flush()

console_handler = SafeStreamHandler()
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

# Функция для запуска бота только в дочернем процессе
def initialize_bot():
    """
    Инициализация и запуск бота, если это дочерний процесс Django.
    """
    if os.environ.get('RUN_MAIN') != 'true':
        # Не запускаем бот в основном процессе (автоматический перезагрузчик)
        logger.debug("Не запускаем бот в основном процессе.")
        return
    else:
        # Запускаем бот в отдельном потоке
        bot_thread = threading.Thread(target=start_bot, daemon=True)
        bot_thread.start()
        logger.info("Поток Telegram бота запущен.")

# Запуск инициализации бота при импорте модуля
initialize_bot()

async def send_order_notification_async(order_data, event="created"):
    """
    Асинхронная функция для отправки уведомления о заказе в Telegram.
    :param order_data: словарь с данными заказа
    :param event: событие ("created" или "status_changed")
    """
    try:
        # Формирование заголовка уведомления
        if event == "created":
            title = "🆕 New Order!"
        elif event == "status_changed":
            title = "🔄 New Order Status"
        else:
            title = "ℹ️ New Information"

        # Формирование текста сообщения
        message_text = (
            f"{title}\n"
            f"Order №{order_data['id']}\n"
            f"Status: {order_data['status']}\n"
            f"Name: {order_data['full_name']}\n"
            f"Phone: {order_data['customer_phone']}\n"
            f"Delivery adress: {order_data['address']}\n\n"
            f"🌺 Flowers:\n"
        )

        # Добавление товаров в сообщение
        for item in order_data['items']:
            product_name = item.product.name
            quantity = item.quantity
            total_price = item.total_price
            message_text += (
                f"  - {product_name} — {quantity} pcs., {total_price} $\n"
            )

        # Общая стоимость заказа
        message_text += f"\n💰 Total Cost: {order_data['total_price']} $"

        # Отправка основного сообщения
        await bot.send_message(chat_id=TELEGRAM_ADMIN_ID, text=message_text)

        # Отправка основного изображения товаров
        sent_images = set()  # Отслеживание уже отправленных изображений, чтобы избежать дубликатов
        for item in order_data['items']:
            if item.product.image_main and item.product.image_main.url not in sent_images:
                await bot.send_photo(
                    chat_id=TELEGRAM_ADMIN_ID,
                    photo=item.product.image_main.url,
                    caption=f"{item.product.name}: {item.total_price} $"
                )
                sent_images.add(item.product.image_main.url)  # Добавляем URL в множество

        logger.info(f"Уведомление для заказа {order_data['id']} отправлено успешно.")

    except TelegramAPIError as e:
        logger.error(f"Ошибка Telegram API при отправке уведомления: {e}")
    except Exception as e:
        logger.error(f"Ошибка при отправке уведомления: {e}")

def send_order_notification(order_data, event="created"):
    """
    Синхронная функция для планирования отправки уведомления о заказе в Telegram.
    :param order_data: словарь с данными заказа
    :param event: событие ("created" или "status_changed")
    """
    try:
        # Планирование асинхронной функции на event loop бота
        asyncio.run_coroutine_threadsafe(
            send_order_notification_async(order_data, event),
            loop
        )
        logger.debug(f"Уведомление для заказа {order_data['id']} запланировано.")
    except Exception as e:
        logger.error(f"Ошибка при планировании уведомления для заказа {order_data['id']}: {e}")
