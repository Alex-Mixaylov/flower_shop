from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Product, Category, BestSeller, TeamMember, Testimonial, Collection, Slide, ComboOffer, Cart, CartItem

from django.db import models
from django.db.models import F

from django.conf import settings
from django.contrib import messages
from django.db.models import Count
from django.db.models import Avg

def index(request):
    # Получение данных для категорий
    categories = Category.objects.annotate(product_count=Count('products'))

    # Получение отзывов
    testimonials = Testimonial.objects.all()

    # Получение слайдов
    slides = Slide.objects.all()

    # Получение данных о Хитах продаж
    best_sellers = BestSeller.objects.filter(is_featured=True).order_by('-created_at')[:10]  # Максимум 10 товаров

    # Добавляем коллекции
    collections = Collection.objects.order_by('-created_at')[:4]  # Последние 4 созданные коллекции

    # Данные для табов "LATEST", "MOST POPULAR", "TOP RATED"
    latest_products = Product.objects.order_by('-created_at')[:4]  # Последние 4 товара
    most_popular_products = Product.objects.filter(is_featured=True).order_by('-created_at')[:4]  # Хиты продаж
    top_rated_products = Product.objects.annotate(average_rating=Avg('rating')).order_by('-average_rating')[:4]  # Товары с высоким рейтингом

    # Расчетные данные для вывода 5 товаров с максимальными скидками
    products_with_discounts = Product.objects.filter(old_price__isnull=False, old_price__gt=F('price')).annotate(discount_amount=F('old_price') - F('price')).order_by('-discount_amount')[:5]

    # Отладочный вывод Расчетные данные для вывода 5 товаров с максимальными скидками
    print("SQL Query:", products_with_discounts.query)  # Проверяет SQL-запрос
    print("Products with Discounts:", products_with_discounts)  # Выводит данные

    # Получение последних 6 товаров для "Gifts worth waiting for"
    combo_offers = ComboOffer.objects.order_by('-id')[:6]  # Выбор последних 6 товаров

    # Получение данных для футера
    footer_context = get_footer_context()

    # Формирование контекста для передачи в шаблон
    context = {
        'categories': categories,
        'testimonials': testimonials,
        'slides': slides,  # Добавление слайдов
        'best_sellers': best_sellers,  # Добавление Хитов продаж
        'collections': collections,  # Коллекции
        'latest_products': latest_products,  # Последние товары
        'most_popular_products': most_popular_products,  # Самые популярные товары
        'top_rated_products': top_rated_products,  # Высокорейтинговые товары
        'products_with_discounts': products_with_discounts, # Товары с максимальной скидкой
        'combo_offers': combo_offers, # Дополнительные товары
        **footer_context,  # Добавление динамических данных в футер
    }
    return render(request, 'orders/index.html', context)


def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    related_products = product.related_products.all()
    combo_offers = product.combo_offers.all()
    return render(request, 'orders/product-details.html', {
        'product': product,
        'reviews': reviews,
        'related_products': related_products,
        'combo_offers': combo_offers,
    })

def shop(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
    }

    return render(request, 'orders/shop.html', context)


def thanks(request):
    # Рендеринг HTML-шаблона thanks.html
    return render(request, 'orders/thanks.html')

def contact(request):
    # Рендеринг HTML-шаблона contact.html
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Формирование HTML-сообщения
        email_message = f"""
        <html>
        <body>
            <table>
                <tr><td>Name</td><td>{name}</td></tr>
                <tr><td>Phone</td><td>{phone}</td></tr>
                <tr><td>Email</td><td>{email}</td></tr>
                <tr><td>Subject</td><td>{subject}</td></tr>
                <tr><td>Message</td><td>{message}</td></tr>
            </table>
        </body>
        </html>
        """

        # Отправка email
        send_mail(
            subject=f"Contact Us - {subject}",
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=['info@example.com'],  # Замените на нужный email
            html_message=email_message,
        )

        return redirect('thanks')  # Перенаправление на страницу благодарности

    return render(request, 'orders/contact.html')

def collections(request):
    collections = Collection.objects.prefetch_related('products').all()
    return render(request, 'orders/collections.html', {'collections': collections})


def collection_detail(request, slug):
    # Получение коллекции по slug
    collection = get_object_or_404(Collection, slug=slug)

    # Получение всех продуктов в этой коллекции
    products = collection.products.all()

    context = {
        'collection': collection,
        'products': products,
    }
    return render(request, 'orders/collection_detail.html', context)

def checkout(request):
    # Рендеринг HTML-шаблона checkout.html
    if request.method == 'POST':
        # Обработка данных формы
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        # Логика сохранения заказа или отправки уведомления
        print(f"Order placed by {name} ({email}), phone: {phone}, address: {address}")
        return redirect('thanks')  # Перенаправление на страницу благодарности
    return render(request, 'orders/checkout.html')

# Корзина
def cart_view(request):
    # Инициализация данных
    cart_items = []
    cart_session = request.session.get('cart', {})
    total_price = 0

    if request.user.is_authenticated:
        # Для авторизованных пользователей
        cart_items = CartItem.objects.filter(user=request.user)  # Получение корзины пользователя
        for item in cart_items:
            # Рассчёт subtotal для каждого элемента
            item.subtotal = item.quantity * item.product.price
            total_price += item.subtotal
    else:
        # Для гостей
        cart_items = []
        for product_id, product_data in cart_session.items():
            product_data['subtotal'] = float(product_data['price']) * product_data['quantity']
            total_price += product_data['subtotal']
            # Создаём структуру, аналогичную записи модели CartItem для шаблона
            cart_items.append({
                'product_id': product_id,
                'name': product_data['name'],
                'quantity': product_data['quantity'],
                'price': product_data['price'],
                'subtotal': product_data['subtotal']
            })

    # Формирование контекста
    context = {
        'cart_items': cart_items,  # Данные корзины
        'total_price': total_price,  # Общая сумма
    }
    return render(request, 'orders/cart.html', context)

# Добавление в Корзину
def add_to_cart(request, product_id):
    # Проверяем наличие product_id
    if not product_id:
        messages.error(request, "Invalid product ID.")
        return redirect('cart')

    # Пытаемся получить продукт, возвращаем 404, если он не найден
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        # Если пользователь авторизован, добавляем в его корзину
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user, product=product
        )
        if not created:
            # Если товар уже в корзине, увеличиваем его количество
            cart_item.quantity += 1
            cart_item.save()
        messages.success(request, f"Товар {product.name} добавлен в корзину.")
    else:
        # Если пользователь не авторизован, используем сессии
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            # Если товар уже в корзине сессии, увеличиваем количество
            cart[str(product_id)]['quantity'] += 1
        else:
            # Если товара нет в корзине, добавляем его
            cart[str(product_id)] = {
                'quantity': 1,
                'name': product.name,
                'price': str(product.price)
            }
        request.session['cart'] = cart
        messages.success(request, f"Товар {product.name} добавлен в корзину.")

    return redirect('cart')

# Удаление из Корзины
def remove_from_cart(request, item_id):
    if not item_id:
        messages.error(request, "Invalid item ID.")
        return redirect('cart')

    if request.user.is_authenticated:
        # Удаление из корзины авторизованного пользователя
        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
        cart_item.delete()
    else:
        # Удаление из корзины в сессии
        cart = request.session.get('cart', {})
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart
    return redirect('cart')

def about(request):
    best_sellers = BestSeller.objects.filter(is_featured=True)
    team_members = TeamMember.objects.all()
    testimonials = Testimonial.objects.all()

    context = {
        'best_sellers': best_sellers,
        'team_members': team_members,
        'testimonials': testimonials,
    }

    return render(request, 'orders/about.html', context)

def get_footer_context():
    # Получение всех коллекций
    collections = Collection.objects.all()

    # Получение всех категорий
    categories = Category.objects.all()

    return {
        'collections': collections,
        'categories': categories,
    }

# для Footer
def shop_by_collection(request, slug):
    collection = get_object_or_404(Collection, slug=slug)
    products = Product.objects.filter(collection=collection)
    context = {
        'collection': collection,
        'products': products,
    }
    return render(request, 'orders/collections.html', context)

def shop_by_category(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(category=category)
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'orders/shop.html', context)
