# apps.py

from django.apps import AppConfig
import os

class OrdersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'orders'

    def ready(self):
        import orders.signals  # Подключение сигналов

        # Инициализация бота только в дочернем процессе
        if os.environ.get('RUN_MAIN') == 'true':
            import bot.bot  # Импортируем бот для запуска