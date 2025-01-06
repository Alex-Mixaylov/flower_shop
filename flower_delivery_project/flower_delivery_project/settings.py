"""
Django settings for flower_delivery_project project.
"""

from pathlib import Path
import os

# --- Основные пути ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Безопасность ---
SECRET_KEY = 'django-insecure-^ho&k%-e(5l-ilxqknk%p@w0qza$#o-ps!&x0ad!a)1pjjh!xi'  # Не используйте это в production!
DEBUG = True  # Включено для разработки. Отключите в production!
ALLOWED_HOSTS = []  # Для разработки оставьте пустым.

# --- Приложения ---
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Custom apps
    'orders',
    'bot',
]

# --- Middleware ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- URL конфигурация ---
ROOT_URLCONF = 'flower_delivery_project.urls'

# --- Шаблоны ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Пустой список, так как используется `APP_DIRS`.
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'orders.context_processors.category_context', # Контекстный процессор для добавления категорий в верхнее меню
            ],
        },
    },
]

# --- WSGI ---
WSGI_APPLICATION = 'flower_delivery_project.wsgi.application'

# --- База данных ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- Валидация паролей ---
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# --- Локализация ---
LANGUAGE_CODE = 'ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- Статические файлы ---
STATIC_URL = '/static/'
#STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATICFILES_DIRS = [
    BASE_DIR / "static"
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Путь для собранных файлов

# --- Медиа файлы ---
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- Кастомная модель пользователя ---
AUTH_USER_MODEL = 'orders.User'

# --- Отправка email (для обратной связи) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.example.com'  # Настройте SMTP-сервер
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'

# --- Django 5.1: Primary key field type ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# settings.py
CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000']
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

