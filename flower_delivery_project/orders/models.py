from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User

from django.utils.text import slugify
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator

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
        Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категория"
    )
    collection = models.ForeignKey(
        Collection, on_delete=models.CASCADE, related_name="products", verbose_name="Коллекция"
    )
    rating = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        verbose_name="Рейтинг"
    )  # Новое поле рейтинга
    is_featured = models.BooleanField(default=False, verbose_name="Показывать на главной странице")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug and self.name:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Cart(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="carts"
    )  # Привязка к пользователю (если авторизован)
    session_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="ID сессии"
    )  # Для неавторизованных пользователей
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

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


# Элементы корзины
class CartItem(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь"
    )  # Добавляем связь с пользователем
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Корзина"
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="cart_items", verbose_name="Товар"
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def total_price(self):
        return self.product.price * self.quantity


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
    title = models.CharField(max_length=255, verbose_name="Название товара")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='bestsellers/', verbose_name="Изображение")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Старая цена")
    tag = models.CharField(max_length=255, blank=True, null=True, verbose_name="Метка (например, категория)")
    is_featured = models.BooleanField(default=False, verbose_name="Показать на главной")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    def __str__(self):
        return self.title

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
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Товар")
    author = models.CharField(max_length=255, verbose_name="Автор")
    rating = models.PositiveIntegerField(verbose_name="Рейтинг", help_text="Укажите рейтинг от 1 до 5")
    text = models.TextField(verbose_name="Текст отзыва")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Отзыв от {self.author} для {self.product.name}"

# Размеры товара
class SizeOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="size_options", verbose_name="Товар")
    size = models.CharField(max_length=50, verbose_name="Размер")
    stems_count = models.PositiveIntegerField(verbose_name="Количество стеблей")

    def __str__(self):
        return f"{self.size} ({self.stems_count} стеблей) - {self.product.name}"

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

# Модель корзины
