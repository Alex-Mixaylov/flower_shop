from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.utils.text import slugify
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.db.models.functions import Substr


# Пользователи (User)
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_admin = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group', related_name='custom_user_set', blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission', related_name='custom_user_set', blank=True
    )

    def __str__(self):
        return self.username

class Collection(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название коллекции")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, verbose_name="URL")
    description = models.TextField(blank=True, null=True, verbose_name="Описание коллекции")
    image = models.ImageField(upload_to='collections/', blank=True, null=True, verbose_name="Изображение коллекции")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


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

# Категория товаров
class Category(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название категории")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, verbose_name="URL")
    description = models.TextField(blank=True, null=True, verbose_name="Описание категории")
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name="Изображение категории")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

# Модель для типа цветов
class FlowerType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# Модель для цвета цветов
class FlowerColor(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название цвета")
    color_code = models.CharField(
        max_length=7,
        verbose_name="Код цвета (HEX)",
        help_text=(
            "Примеры HEX-кодов:<br>"
            "<strong>Красный:</strong> #FF0000<br>"
            "<strong>Белый:</strong> #FFFFFF<br>"
            "<strong>Желтый:</strong> #FFFF00<br>"
            "<strong>Черный:</strong> #000000<br>"
            "<strong>Салатовый:</strong> #32CD32<br>"
            "<strong>Оранжевый:</strong> #FFA500<br>"
            "<strong>Фиолетовый:</strong> #800080<br>"
            "<strong>Синий:</strong> #0000FF"
        )
    )

    def __str__(self):
        return self.name

# Товары
class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название товара")
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание")
    image_main = models.ImageField(upload_to='products/', verbose_name="Основное изображение")
    image_secondary = models.ImageField(
        upload_to='products/', blank=True, null=True, verbose_name="Дополнительное изображение"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Старая цена")
    category = models.ForeignKey(
        'Category', on_delete=models.CASCADE, related_name="products", verbose_name="Категория"
    )
    collection = models.ForeignKey(
        'Collection', on_delete=models.CASCADE, related_name="products", verbose_name="Коллекция"
    )
    rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Рейтинг"
    )
    is_featured = models.BooleanField(default=False, verbose_name="Показывать на главной странице")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    # Новые поля для связей с FlowerType и FlowerColor
    flower_types = models.ManyToManyField(
        'FlowerType', related_name='products', blank=True, verbose_name="Типы цветов"
    )
    flower_colors = models.ManyToManyField(
        'FlowerColor', related_name='products', blank=True, verbose_name="Цвета цветов"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    # Метод для поиска связанных товаров по входжению slug в url
    # и поиска связанных товаров (вариаций)
    def get_related_products(self):
        # Получаем основную часть slug без количества стеблей
        base_slug = '-'.join(self.slug.split('-')[:-1])

        # Ищем товары с таким же base_slug
        return Product.objects.filter(slug__startswith=base_slug).exclude(id=self.id)

# Корзина
class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Поддержка кастомной модели пользователя
        on_delete=models.SET_NULL,  # Корзина сохраняется даже если пользователь удален
        null=True,
        blank=True,
        related_name='cart',
        verbose_name="Пользователь"
    )
    session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии"
    )  # Для неавторизованных пользователей
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")  # Отслеживание изменений

    def __str__(self):
        user_info = f"User: {self.user.username}" if self.user else "Session"
        return f"Cart #{self.id} ({user_info})"

    def total_price(self):
        """
        Calculate the total price of items in the cart.
        """
        return sum(item.total_price() for item in self.items.all())

    total_price.short_description = "Total Price"

    def total_items(self):
        """
        Calculate the total number of items in the cart.
        """
        return sum(item.quantity for item in self.items.all())

    total_items.short_description = "Total Items"

    def item_count(self):
        """
        Alias for total_items to use in admin or other visual representation.
        """
        return self.total_items()

    item_count.short_description = "Item Count"  # Отображение в админке

# Элемент Корзины
class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Корзина"
    )  # Связь с корзиной
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Товар"
    )  # Связь с товаром
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        """
        Calculate the total price for the cart item.
        """
        return self.product.price * self.quantity

    total_price.short_description = "Total Price"

    def get_cart_user(self):
        """
        Returns the user associated with the cart, if any.
        """
        return self.cart.user

    get_cart_user.short_description = "Cart User"

    def is_for_guest(self):
        """
        Check if the cart item belongs to a guest (not linked to a user).
        """
        return self.cart.user is None


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
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders') #Корзина

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

# Лучшие товары (Best Sellers)
class BestSeller(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="best_sellers",
        verbose_name="Товар"
    )
    tag = models.CharField(max_length=255, blank=True, null=True, verbose_name="Метка (например, категория)")
    is_featured = models.BooleanField(default=False, verbose_name="Показать на главной")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = "Лучший товар"
        verbose_name_plural = "Лучшие товары"


# Команда (Team)
class TeamMember(models.Model):
    name = models.CharField(max_length=255, verbose_name="Имя")
    role = models.CharField(max_length=255, verbose_name="Роль")
    photo = models.ImageField(upload_to='team/', verbose_name="Фотография")

    def __str__(self):
        return self.name

# Общие отзывы (Testimonials)
class Testimonial(models.Model):
    author = models.CharField(max_length=255, verbose_name="Автор")
    text = models.TextField(verbose_name="Отзыв")
    photo = models.ImageField(upload_to='testimonials/', verbose_name="Фотография автора")

    def __str__(self):
        return self.author


# Отзывы о продуктах
class Review(models.Model):
    # Связь с моделью продукта
    product = models.ForeignKey(
        'Product',
        related_name='reviews',
        on_delete=models.CASCADE,
        verbose_name="Товар"
    )
    # Связь с пользователем
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    # Поле рейтинга с валидаторами и диапазоном от 1 до 5
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Рейтинг",
        help_text="Укажите рейтинг от 1 до 5"
    )
    # Текст отзыва
    text = models.TextField(verbose_name="Текст отзыва")
    # Дата создания отзыва
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    # Статус одобрения отзыва
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен")

    # Метод очистки данных (валидация)
    def clean(self):
        # Проверка на указание продукта
        if not self.product_id:
            raise ValidationError('Продукт должен быть указан.')

        # Если это новая запись (нет PK), а отзыв уже существует
        # (тем самым блокируем только попытку «создать дубль»,
        #  но позволяем редактировать уже существующий отзыв)
        if not self.pk and Review.objects.filter(product=self.product, author=self.author).exists():
            raise ValidationError('Вы уже оставили отзыв для этого товара. Пожалуйста, отредактируйте его, '
                                  'вместо создания нового.')

    # Представление объекта в виде строки
    def __str__(self):
        return f'{self.author.username} - {self.product.name} ({self.rating} звёзд)'

    # Метод для получения статуса одобрения
    @property
    def status(self):
        return "Одобрен" if self.is_approved else "На модерации"


# Количество стеблей в букете
class SizeOption(models.Model):
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE, related_name="size_option", unique=True, verbose_name="Товар"
    )
    size = models.CharField(max_length=50, verbose_name="Размер")
    stems_count = models.PositiveIntegerField(verbose_name="Количество стеблей")

    def __str__(self):
        return f"{self.size} ({self.stems_count} стеблей)"


# Связанные товары
class RelatedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="related_products",
                                verbose_name="Товар")
    related_product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="related_to",
                                        verbose_name="Связанный товар")

    def __str__(self):
        return f"Связанный товар: {self.related_product.name} для {self.product.name}"


# Комплектующие/Дополнительные товары
class ComboOffer(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="combo_offers", verbose_name="Товар")
    name = models.CharField(max_length=255, verbose_name="Название дополнения")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена дополнения")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Старая цена")
    image = models.ImageField(upload_to='combos/', verbose_name="Изображение дополнения")

    def __str__(self):
        return f"{self.name} для {self.product.name}"


#Управление слайдером

class Slide(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Описание")
    main_image = models.ImageField(upload_to='slides/', verbose_name="Основное изображение")
    background_image = models.ImageField(upload_to='slides/', blank=True, null=True, verbose_name="Фоновое изображение")
    additional_image = models.ImageField(upload_to='slides/', blank=True, null=True, verbose_name="Дополнительное изображение")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        ordering = ['order']
        verbose_name = "Слайд"
        verbose_name_plural = "Слайды"

    def __str__(self):
        return self.title


