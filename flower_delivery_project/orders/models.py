from django.db import models
from django.contrib.auth.models import AbstractUser


# Пользователи (User)
class User(AbstractUser):
    # Наследуется от AbstractUser, чтобы использовать стандартные функции Django для аутентификации
    email = models.EmailField(unique=True)  # Уникальный email для каждого пользователя
    phone = models.CharField(max_length=15, blank=True, null=True)  # Номер телефона пользователя
    is_admin = models.BooleanField(default=False)  # Флаг для определения, является ли пользователь администратором

    def __str__(self):
        return self.username


# Коллекции (Collection)
class Collection(models.Model):
    # Хранит данные о коллекциях товаров (например, Розы, Букеты)
    name = models.CharField(max_length=255)  # Название коллекции
    description = models.TextField(blank=True, null=True)  # Описание коллекции

    def __str__(self):
        return self.name


# Букеты (Bouquet)
class Bouquet(models.Model):
    # Основная модель для хранения информации о товарах
    name = models.CharField(max_length=255)  # Название букета
    description = models.TextField(blank=True, null=True)  # Описание букета
    image = models.ImageField(upload_to='bouquets/', blank=True, null=True)  # Путь к изображению букета
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена букета
    stock = models.IntegerField(default=0)  # Количество товара на складе
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='bouquets')
    # Связь с коллекцией. Если коллекция удаляется, букеты тоже удаляются.
    # related_name='bouquets' позволяет получать все букеты коллекции через collection.bouquets.all()

    def __str__(self):
        return self.name


# Заказы (Order)
class Order(models.Model):
    # Модель для хранения информации о заказах
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),  # В ожидании
        ('IN_PROGRESS', 'In Progress'),  # В работе
        ('PAID', 'Paid'),  # Оплачен
        ('READY', 'Ready'),  # Готов
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    # Связь с пользователем, который сделал заказ. Если пользователь удалён, заказы сохраняются.
    customer_name = models.CharField(max_length=255)  # Имя клиента (для неавторизованных пользователей)
    customer_email = models.EmailField()  # Email клиента (для неавторизованных пользователей)
    customer_phone = models.CharField(max_length=15)  # Номер телефона клиента
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')  # Статус заказа
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # Общая стоимость заказа
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время создания заказа

    def __str__(self):
        return f"Order #{self.id} - {self.status}"


# Элементы заказа (OrderItem)
class OrderItem(models.Model):
    # Модель для хранения данных о конкретных товарах в заказе
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    # Связь с заказом. Если заказ удаляется, элементы тоже удаляются.
    bouquet = models.ForeignKey(Bouquet, on_delete=models.CASCADE, related_name='order_items')
    # Связь с букетом. Если букет удаляется, элементы заказа тоже удаляются.
    quantity = models.PositiveIntegerField(default=1)  # Количество данного букета в заказе
    item_price = models.DecimalField(max_digits=10, decimal_places=2)  # Цена букета на момент заказа

    def __str__(self):
        return f"{self.quantity} x {self.bouquet.name}"


# Сообщения из формы контактов (ContactMessage)
class ContactMessage(models.Model):
    # Модель для хранения сообщений, отправленных пользователями через форму контактов
    name = models.CharField(max_length=255)  # Имя отправителя
    email = models.EmailField()  # Email отправителя
    message = models.TextField()  # Сообщение
    created_at = models.DateTimeField(auto_now_add=True)  # Дата и время отправки сообщения

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
