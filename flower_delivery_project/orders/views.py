from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import (
    CustomUser, Product, FlowerType, FlowerColor, SizeOption, Category,
    BestSeller, TeamMember, Testimonial, Review, Collection, Slide,
    ComboOffer, Cart, CartItem, Order, OrderItem, Delivery
)
from .forms import ReviewForm, DeliveryForm, CheckoutForm

from django.db.models import F
from django.db.models import Q

from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.urls import reverse

from django.db.models import Count, Avg, Sum

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import logging
logger = logging.getLogger('orders')

from django.contrib.auth.decorators import login_required


# Главная страница
def index(request):
    logger.debug("Initiating index view.")

    # Получение данных для категорий на Главной не из контекст-процессора
    categories_index = Category.objects.annotate(product_count=Count('products'))
    logger.debug(f"Retrieved {categories_index.count()} categories with product counts.")

    # Получение отзывов
    testimonials = Testimonial.objects.all()
    logger.debug(f"Retrieved {testimonials.count()} testimonials.")

    # Получение слайдов
    slides = Slide.objects.all()
    logger.debug(f"Retrieved {slides.count()} slides.")

    # Получение данных о Хитах продаж
    best_sellers = BestSeller.objects.filter(is_featured=True).order_by('-created_at')[:10]  # Максимум 10 товаров
    logger.debug(f"Retrieved {best_sellers.count()} featured best sellers.")

    # Добавляем коллекции
    collections = Collection.objects.order_by('-created_at')[:4]  # Последние 4 созданные коллекции
    logger.debug(f"Retrieved {collections.count()} latest collections.")

    # Данные для табов "LATEST", "MOST POPULAR", "TOP RATED"
    latest_products = Product.objects.order_by('-created_at')[:4]  # Последние 4 товара
    logger.debug(f"Retrieved {latest_products.count()} latest products.")

    most_popular_products = Product.objects.filter(is_featured=True).order_by('-created_at')[:4]  # Хиты продаж
    logger.debug(f"Retrieved {most_popular_products.count()} most popular products.")

    top_rated_products = Product.objects.annotate(average_rating=Avg('rating')).order_by('-average_rating')[:4]  # Товары с высоким рейтингом
    logger.debug(f"Retrieved {top_rated_products.count()} top-rated products.")

    # Расчетные данные для вывода 5 товаров с максимальными скидками
    products_with_discounts = Product.objects.filter(
        old_price__isnull=False,
        old_price__gt=F('price')
    ).annotate(
        discount_amount=F('old_price') - F('price')
    ).order_by('-discount_amount')[:5]
    logger.debug("SQL Query: %s", products_with_discounts.query)  # Проверяет SQL-запрос
    logger.debug("Products with Discounts: %s", products_with_discounts)  # Выводит данные

    # Получение последних 6 товаров для "Gifts worth waiting for"
    combo_offers = ComboOffer.objects.order_by('-id')[:6]  # Выбор последних 6 товаров
    logger.debug(f"Retrieved {combo_offers.count()} combo offers.")

    # Получение данных для футера
    footer_context = get_footer_context()
    logger.debug("Retrieved footer context.")

    # Формирование контекста для передачи в шаблон
    context = {
        'categories_index': categories_index,
        'testimonials': testimonials,
        'slides': slides,  # Добавление слайдов
        'best_sellers': best_sellers,  # Добавление Хитов продаж
        'collections': collections,  # Коллекции
        'latest_products': latest_products,  # Последние товары
        'most_popular_products': most_popular_products,  # Самые популярные товары
        'top_rated_products': top_rated_products,  # Высокорейтинговые товары
        'products_with_discounts': products_with_discounts,  # Товары с максимальной скидкой
        'combo_offers': combo_offers,  # Дополнительные товары
        **footer_context,  # Добавление динамических данных в футер
    }
    logger.debug("Rendering index.html with context.")
    return render(request, 'orders/index.html', context)


# Регистрация нового пользователя
@csrf_exempt
def register(request):
    logger.debug("Initiating register view.")
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirmpassword = request.POST.get('confirmpassword', '').strip()

        logger.debug(f"Registration attempt with fullname: {fullname}, email: {email}")

        # Проверка заполненности полей
        if not fullname or not email or not password or not confirmpassword:
            logger.warning("Registration failed: All fields are required.")
            return JsonResponse({'success': False, 'error': 'All fields are required.'})

        # Проверка совпадения паролей
        if password != confirmpassword:
            logger.warning("Registration failed: Passwords do not match.")
            return JsonResponse({'success': False, 'error': 'Passwords do not match.'})

        UserModel = get_user_model()  # Получаем текущую модель (CustomUser, если она в settings)

        # Проверка существующего пользователя
        if UserModel.objects.filter(username=fullname).exists():
            logger.warning(f"Registration failed: Username '{fullname}' already exists.")
            return JsonResponse({'success': False, 'error': 'Username already exists.'})

        if UserModel.objects.filter(email=email).exists():
            logger.warning(f"Registration failed: Email '{email}' is already registered.")
            return JsonResponse({'success': False, 'error': 'Email is already registered.'})

        # Создание пользователя
        user = UserModel.objects.create_user(username=fullname, email=email, password=password)
        user.save()
        logger.info(f"User '{fullname}' registered successfully.")

        return JsonResponse({'success': True, 'message': 'Registration successful! Please log in.'})

    logger.warning("Registration failed: Invalid request method.")
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


# Страница товара и добавление отзыва
def product_details(request, slug):
    logger.debug(f"Initiating product_details view for slug: {slug}")

    # Получаем текущий продукт по slug
    product = get_object_or_404(Product, slug=slug)
    logger.debug(f"Retrieved product: {product.name}")

    # Отладочная печать информации о текущем пользователе
    logger.debug("DEBUG request.user = %s", request.user)
    logger.debug("DEBUG request.user.is_authenticated = %s", request.user.is_authenticated)
    logger.debug(
        "DEBUG request.user.id = %s",
        request.user.id if request.user.is_authenticated else None
    )
    logger.debug(
        "DEBUG request.user._meta.model = %s",
        request.user._meta.model if request.user.is_authenticated else None
    )

    # Получаем все одобренные отзывы для текущего продукта
    reviews = Review.objects.filter(product=product, is_approved=True)
    logger.debug(f"Retrieved {reviews.count()} approved reviews for product '{product.name}'.")

    # Получаем рейтинговые продукты для товарного виджета
    top_rated_products = Product.objects.filter(rating__gte=4).order_by('-rating')[:4]
    logger.debug(f"Retrieved {top_rated_products.count()} top-rated products for widget.")

    # Получаем связанные продукты с разным количеством стеблей
    related_products = product.get_related_products()
    related_products_with_stems = [
        {
            'name': related_product.name,
            'slug': related_product.slug,
            'stems': related_product.slug.split('-')[-1],
            'is_active': related_product == product,
        }
        for related_product in related_products
    ]
    logger.debug(f"Retrieved {len(related_products_with_stems)} related products with stems.")

    # Добавляем текущий продукт в список вариаций, если его там еще нет
    if product.slug not in [p['slug'] for p in related_products_with_stems]:
        related_products_with_stems.append({
            'name': product.name,
            'slug': product.slug,
            'stems': product.slug.split('-')[-1],
            'is_active': True,
        })
        logger.debug(f"Added current product '{product.name}' to related products with stems.")

    # Здесь объявляем переменную с количеством стеблей
    product_stems = product.slug.split('-')[-1]
    logger.debug(f"Product stems count: {product_stems}")

    # === Новая часть: ищем существующий отзыв для редактирования ===
    existing_review = None
    if request.user.is_authenticated:
        existing_review = Review.objects.filter(product=product, author=request.user).first()
        if existing_review:
            logger.debug(f"Existing review found for user '{request.user.username}' on product '{product.name}'.")
        else:
            logger.debug(f"No existing review found for user '{request.user.username}' on product '{product.name}'.")

    if existing_review:
        # Режим "редактирования" уже существующего отзыва
        form = ReviewForm(request.POST or None, instance=existing_review)
        logger.debug("Initialized ReviewForm for editing existing review.")
    else:
        # Режим "создания" нового отзыва
        form = ReviewForm(request.POST or None)
        logger.debug("Initialized ReviewForm for creating new review.")

    # Назначаем product
    form.instance.product = product
    logger.debug(f"Assigned product '{product.name}' to review form.")

    # Назначаем author, если пользователь авторизован
    if request.user.is_authenticated:
        form.instance.author = request.user
        logger.debug(f"Assigned author '{request.user.username}' to review form.")

        if request.method == 'POST':
            if form.is_valid():
                review = form.save(commit=False)
                review.save()
                logger.info(f"Review by user '{request.user.username}' for product '{product.name}' saved successfully.")
                messages.success(request, 'Your review has been submitted successfully!')
                return redirect('product_details', slug=slug)
            else:
                logger.warning(f"Review form is invalid for user '{request.user.username}'.")
                messages.error(request, 'There were errors in your form. Please check below.')
    else:
        logger.warning("Attempt to submit review by unauthenticated user.")
        messages.error(request, 'You must be logged in to leave a review.')

    # Передаем данные в шаблон для отображения
    return render(request, 'orders/product-details.html', {
        'product': product,
        'reviews': reviews,
        'related_products_with_stems': related_products_with_stems,
        'form': form,
        'product_stems': product_stems,
        'top_rated_products': top_rated_products,
    })


# Каталог на сайте
def shop(request):
    logger.debug("Initiating shop view.")

    # Получение всех фильтров
    category_ids = request.GET.getlist('categories')  # Список ID категорий
    min_price = request.GET.get('min_price')  # Минимальная цена
    max_price = request.GET.get('max_price')  # Максимальная цена
    flower_type_ids = request.GET.getlist('flower_types')  # Список ID типов цветов
    flower_color_ids = request.GET.getlist('flower_colors')  # Список ID цветов цветов
    query = request.GET.get('q')  # Поисковый запрос

    logger.debug(
        f"Shop filters - Categories: {category_ids}, Flower Types: {flower_type_ids}, "
        f"Flower Colors: {flower_color_ids}, Price Range: {min_price} - {max_price}, Query: {query}"
    )

    # Базовый QuerySet для всех продуктов
    products_list = Product.objects.all().order_by('id')  # Добавляем сортировку по ID для пагинации
    logger.debug(f"Initial products_list count: {products_list.count()}")

    # Фильтрация по категориям
    if category_ids:
        products_list = products_list.filter(category__id__in=category_ids)
        logger.debug(f"Filtered products by categories: {category_ids}, new count: {products_list.count()}")

    # Фильтрация по ценовому диапазону
    if min_price and max_price:
        products_list = products_list.filter(price__gte=min_price, price__lte=max_price)
        logger.debug(f"Filtered products by price range: {min_price} - {max_price}, new count: {products_list.count()}")

    # Фильтрация по типу цветов
    if flower_type_ids:
        products_list = products_list.filter(flower_types__id__in=flower_type_ids)
        logger.debug(f"Filtered products by flower types: {flower_type_ids}, new count: {products_list.count()}")

    # Фильтрация по цвету цветов
    if flower_color_ids:
        products_list = products_list.filter(flower_colors__id__in=flower_color_ids)
        logger.debug(f"Filtered products by flower colors: {flower_color_ids}, new count: {products_list.count()}")

    # Фильтрация по поисковому запросу (поиск по названию товаров)
    if query:
        products_list = products_list.filter(Q(name__icontains=query))  # Фильтруем по названию (регистр не важен)
        logger.debug(f"Filtered products by search query: '{query}', new count: {products_list.count()}")

    # --- ДОБАВЛЯЕМ: проверка GET-параметра favorites ---
    if request.GET.get('favorites') == '1':
        fav_ids = request.session.get('favorites', [])
        logger.debug(f"Filtering only favorites: {fav_ids}")
        if fav_ids:
            products_list = products_list.filter(id__in=fav_ids)
        else:
            products_list = Product.objects.none()  # Пустой набор, если избранное пустое
    # --- КОНЕЦ добавляемого блока ---

    # Удаление дублирующихся продуктов (если фильтры приводят к повторным объектам)
    products_list = products_list.distinct()
    logger.debug(f"After distinct filter, products_list count: {products_list.count()}")

    # Пагинация
    paginator = Paginator(products_list, 9)  # По 9 товаров на страницу
    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
        logger.debug(f"Paginated to page {page_number}, products count: {products.object_list.count()}")
    except PageNotAnInteger:
        products = paginator.page(1)  # Если номер страницы не число, показать первую страницу
        logger.debug("Page number not an integer. Showing first page.")
    except EmptyPage:
        products = paginator.page(paginator.num_pages)  # Если страница пуста, показать последнюю страницу
        logger.debug("Empty page. Showing last page.")

    # Контекст для передачи данных в шаблон
    context = {
        'products': products,
        'categories': Category.objects.all(),
        'flower_types': FlowerType.objects.all(),
        'flower_colors': FlowerColor.objects.all(),
        'selected_categories': category_ids,
        'selected_flower_types': flower_type_ids,
        'selected_flower_colors': flower_color_ids,
        'min_price': min_price,
        'max_price': max_price,
        'query': query,  # Передаём поисковый запрос в шаблон
    }
    logger.debug("Rendering shop.html with context.")
    return render(request, 'orders/shop.html', context)


def contact(request):
    logger.debug("Initiating contact view.")

    # Рендеринг HTML-шаблона contact.html
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        logger.debug(f"Contact form submitted by {name} with email {email}.")

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
        try:
            send_mail(
                subject=f"Contact Us - {subject}",
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=['info@example.com'],  # Замените на нужный email
                html_message=email_message,
            )
            logger.info(f"Contact email sent successfully from {email}.")
        except Exception as e:
            logger.error(f"Failed to send contact email from {email}: {e}")
            messages.error(request, "There was an error sending your message. Please try again later.")
            return redirect('contact')

        return redirect('thanks')  # Перенаправление на страницу благодарности

    logger.debug("Rendering contact.html with GET request.")
    return render(request, 'orders/contact.html')


def collections(request):
    logger.debug("Initiating collections view.")

    collections = Collection.objects.prefetch_related('products').all()
    logger.debug(f"Retrieved {collections.count()} collections with related products.")

    return render(request, 'orders/collections.html', {'collections': collections})


def collection_detail(request, slug):
    logger.debug(f"Initiating collection_detail view for slug: {slug}")

    # Получение коллекции по slug
    collection = get_object_or_404(Collection, slug=slug)
    logger.debug(f"Retrieved collection: {collection.name}")

    # Получение всех продуктов в этой коллекции
    products = collection.products.all()
    logger.debug(f"Retrieved {products.count()} products in collection '{collection.name}'.")

    context = {
        'collection': collection,
        'products': products,
    }
    logger.debug("Rendering collection_detail.html with context.")
    return render(request, 'orders/collection_detail.html', context)


# Определяем простой класс для имитации объекта Product для гостей
class ProductMock:
    def __init__(self, name):
        self.name = name
# Размещение заказа
def checkout(request):
    """
    Страница оформления заказа
    """
    logger.debug("Initiating checkout view.")

    user = request.user
    logger.debug(f"User: {user.username if user.is_authenticated else 'Guest'}")

    # Получить session_id для гостя
    session_id = request.session.session_key
    if not session_id:
        request.session.create()
        session_id = request.session.session_key
        logger.debug("Created new session.")
    logger.debug(f"Session ID: {session_id}")

    # Проверить аутентификацию пользователя
    logger.debug(f"User Authenticated: {user.is_authenticated}")

    if user.is_authenticated:
        logger.debug(f"Authenticated User ID: {user.id}")
        logger.debug(f"Authenticated Username: {user.username}")
        # Получение корзины для авторизованного пользователя
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            logger.debug(f"Created new cart for user {user.username}: Cart ID {cart.id}")
        else:
            logger.debug(f"Retrieved existing cart for user {user.username}: Cart ID {cart.id}")

        if cart.items.exists():
            logger.debug(f"Cart {cart.id} has {cart.items.count()} items.")
        else:
            logger.warning(f"Cart {cart.id} for user {user.username} is empty.")

        for item in cart.items.all():
            logger.debug(f"Cart item: {item}")

        # Определение cart_items и total_price для авторизованных пользователей
        cart_items = cart.items.all()
        total_price = sum(item.product.price * item.quantity for item in cart.items.all())
    else:
        logger.debug("User is not authenticated.")
        # Получение корзины из session['cart']
        cart_data = request.session.get('cart', {})
        if cart_data:
            logger.debug(f"Guest has {len(cart_data)} items in cart.")
        else:
            logger.warning(f"No cart found for session {session_id}.")
            logger.debug(f"Current session cart data: {cart_data}")

        # Определение cart_items и total_price для гостей
        cart_items = [
            {
                'product': ProductMock(name=data['name']),
                'quantity': data['quantity'],
                'total_price': data['price'] * data['quantity'],
            }
            for pid, data in cart_data.items()
        ]
        total_price = sum(item['total_price'] for item in cart_items)
        logger.debug(f"Total price calculated: ${total_price}")
        logger.debug(f"Cart items for template: {cart_items}")  # Дополнительная отладка

    # Проверка на наличие товаров в корзине
    if user.is_authenticated:
        if not cart.items.exists():
            logger.error(f"Cart items count: {cart.items.count()}")
            messages.error(request, "Your cart is empty.")
            return redirect('cart')
    else:
        if not cart_data:
            logger.error("Cart data is empty for guest.")
            messages.error(request, "Your cart is empty.")
            return redirect('cart')

    if request.method == 'POST':
        logger.debug("Processing POST request for checkout.")
        checkout_form = CheckoutForm(request.POST)
        delivery_form = DeliveryForm(request.POST)

        if checkout_form.is_valid() and delivery_form.is_valid():
            logger.debug("Checkout and Delivery forms are valid.")
            try:
                with transaction.atomic():
                    # Создание заказа
                    order = checkout_form.save(commit=False)
                    order.user = user if user.is_authenticated else None

                    if user.is_authenticated:
                        order.total_price = sum(item.product.price * item.quantity for item in cart.items.all())
                    else:
                        order.total_price = sum(item['total_price'] for item in cart_items)

                    order.save()
                    logger.info(
                        f"Order #{order.id} created for user {user.username if user.is_authenticated else 'Guest'} with total price ${order.total_price}."
                    )

                    # Создание данных доставки
                    delivery = delivery_form.save(commit=False)
                    delivery.order = order
                    delivery.save()
                    logger.debug(f"Delivery information saved for Order #{order.id}.")

                    # Переносим элементы корзины в заказ
                    if user.is_authenticated:
                        for item in cart.items.all():
                            OrderItem.objects.create(
                                order=order,
                                product=item.product,
                                quantity=item.quantity,
                                item_price=item.product.price
                            )
                            logger.debug(
                                f"OrderItem created: {item.quantity} x {item.product.name} at ${item.product.price} each."
                            )

                        # Очистка корзины
                        cart.items.all().delete()
                        logger.debug(f"Cart #{cart.id} cleared after order placement.")
                    else:
                        for product_id, item in cart_data.items():
                            try:
                                product = Product.objects.get(id=product_id)
                                OrderItem.objects.create(
                                    order=order,
                                    product=product,
                                    quantity=item['quantity'],
                                    item_price=item['price']
                                )
                                logger.debug(
                                    f"OrderItem created: {item['quantity']} x {product.name} at ${item['price']} each."
                                )
                            except Product.DoesNotExist:
                                logger.error(f"Product with ID {product_id} does not exist. Skipping.")

                        # Очистка корзины
                        del request.session['cart']
                        request.session.modified = True
                        logger.debug("Guest cart cleared after order placement.")

                messages.success(request, "Your order has been placed successfully.")
                redirect_url = f'{reverse("thanks")}?customer_name={order.delivery.full_name}&order_id={order.id}'
                logger.debug(f"Redirecting to thanks page: {redirect_url}")
                return redirect(redirect_url)
            except Exception as e:
                logger.error(f"Unexpected error during checkout: {e}")
                messages.error(request, "There was an error processing your order. Please try again.")
        else:
            logger.warning("Checkout or Delivery form is invalid.")
            messages.error(request, "There were errors in your form. Please check below.")
    else:
        logger.debug("Rendering checkout page with GET request.")
        checkout_form = CheckoutForm()
        delivery_form = DeliveryForm()

    return render(request, 'orders/checkout.html', {
        'checkout_form': checkout_form,
        'delivery_form': delivery_form,
        'cart_items': cart_items,
        'total_price': total_price,
    })

# Успешное размещение заказа
def thanks(request):
    """
    Страница благодарности после размещения заказа.
    """
    customer_name = request.GET.get('customer_name', 'Valued Customer')
    order_id = request.GET.get('order_id', 'Unknown Order')
    logger.debug(f"Rendering thanks page for customer '{customer_name}' and order ID '{order_id}'.")
    return render(request, 'orders/thanks.html', {
        'customer_name': customer_name,
        'order_id': order_id,
    })


# Корзина
def cart_view(request):
    logger.debug("cart_view has been called.")

    cart_items = []
    total_price = 0

    user = request.user
    logger.debug("Initiating cart_view.")
    logger.debug(f"User: {user.username if user.is_authenticated else 'Guest'}")

    if user.is_authenticated:
        logger.debug(f"User is authenticated: {user.username}")
        # Получение корзины пользователя
        cart, created = Cart.objects.get_or_create(user=user)
        if created:
            logger.debug(f"Created new cart for user {user.username}: Cart ID {cart.id}")
        else:
            logger.debug(f"Retrieved existing cart for user {user.username}: Cart ID {cart.id}")

        if cart.items.exists():
            logger.debug(f"Cart {cart.id} has {cart.items.count()} items.")
        else:
            logger.warning(f"Cart {cart.id} for user {user.username} is empty.")

        for item in cart.items.select_related('product'):
            size_option = item.product.size_option
            cart_items.append({
                'product_id': item.product.id,
                'name': item.product.name,
                'quantity': item.quantity,
                'price': item.product.price,
                'old_price': item.product.old_price,
                'image_main': item.product.image_main.url if item.product.image_main else None,
                'size': size_option.size if size_option else "N/A",
                'stems_count': size_option.stems_count if size_option else 0,
            })
            logger.debug(
                f"Cart Item - ID: {item.id}, Product: {item.product.name}, Price: {item.product.price}, Size: {size_option.size if size_option else 'N/A'}"
            )
            total_price += item.total_price()
    else:
        logger.debug("User is not authenticated.")
        # Для гостей
        cart_session = request.session.get('cart', {})
        logger.debug(f"Session cart data: {cart_session}")
        if cart_session:
            logger.debug(f"Guest has {len(cart_session)} items in cart.")
        else:
            logger.warning("Guest cart is empty.")
        for product_id, product_data in cart_session.items():
            try:
                product = Product.objects.get(id=product_id)
                size_option = product.size_option
                subtotal = float(product_data['price']) * float(product_data['quantity'])
                total_price += subtotal
                cart_items.append({
                    'product_id': product_id,
                    'name': product_data.get('name', 'Unknown Product'),
                    'quantity': product_data.get('quantity', 1),
                    'price': float(product_data['price']),
                    'old_price': float(product_data.get('old_price', 0)),
                    'image_main': product_data.get('image_main'),
                    'size': size_option.size if size_option else "N/A",
                    'stems_count': size_option.stems_count if size_option else 0,
                })
                logger.debug(
                    f"Guest Cart Item - ID: {product_id}, Product: {product.name}, Size: {size_option.size if size_option else 'N/A'}"
                )
            except Product.DoesNotExist:
                logger.error(f"Product with ID {product_id} does not exist. Skipping.")

    # Отладочный вывод
    logger.debug(f"Total Price: ${total_price:.2f}")

    # Получение топовых продуктов
    top_rated_products = Product.objects.filter(rating__gte=4).order_by('-rating')[:4]
    logger.debug(f"Retrieved {top_rated_products.count()} top-rated products.")

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'top_rated_products': top_rated_products,
    }
    logger.debug("Rendering cart.html with context.")
    return render(request, 'orders/cart.html', context)


def add_to_cart(request, product_id):
    """
    Функция добавления товара в корзину.
    Работает как для зарегистрированных пользователей, так и для гостей.
    Учитывает количество товара, переданное в POST-запросе.
    """
    logger.debug(f"Initiating add_to_cart view for product_id: {product_id}")

    product = get_object_or_404(Product, id=product_id)
    logger.debug(f"Retrieved product: {product.name}")

    # Получаем количество товара из POST-запроса (по умолчанию 1, если не передано)
    quantity = int(request.POST.get('quantity', 1))
    logger.debug(f"Adding quantity {quantity} for product '{product.name}'.")

    if request.user.is_authenticated:
        # Корзина для зарегистрированных пользователей
        cart, created = Cart.objects.get_or_create(user=request.user)
        if created:
            logger.debug(f"Created new cart for user {request.user.username}: Cart ID {cart.id}")
        else:
            logger.debug(f"Retrieved existing cart for user {request.user.username}: Cart ID {cart.id}")

        # Проверяем, есть ли уже этот товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}  # Используем переданное количество для нового товара
        )

        if not created:
            # Если товар уже есть в корзине, увеличиваем количество
            old_quantity = cart_item.quantity
            cart_item.quantity += quantity
            cart_item.save()
            logger.debug(
                f"Updated quantity for product '{product.name}' in user '{request.user.username}' cart from {old_quantity} to {cart_item.quantity}."
            )
        else:
            logger.debug(
                f"Added new product '{product.name}' with quantity {quantity} to user '{request.user.username}' cart."
            )

    else:
        # Корзина для гостей
        cart = request.session.get('cart', {})
        if str(product_id) in cart:
            # Если товар уже есть в корзине, увеличиваем количество
            old_quantity = cart[str(product_id)]['quantity']
            cart[str(product_id)]['quantity'] += quantity
            logger.debug(
                f"Updated quantity for product '{product.name}' in guest cart from {old_quantity} to {cart[str(product_id)]['quantity']}."
            )
        else:
            # Если товара нет в корзине, добавляем его с указанным количеством
            cart[str(product_id)] = {
                'quantity': quantity,
                'name': product.name,
                'price': round(float(product.price), 2),
                'old_price': round(float(product.old_price), 2) if product.old_price else None,
                'image_main': product.image_main.url if product.image_main else None,
            }
            logger.debug(f"Added new product '{product.name}' with quantity {quantity} to guest cart.")

        # Сохраняем корзину в сессию
        request.session['cart'] = cart
        logger.debug("Guest cart updated in session.")

    # Отправляем JSON-ответ с подтверждением добавления товара и его количеством
    logger.debug("Returning JSON response for add_to_cart.")
    return JsonResponse({
        'message': 'Товар успешно добавлен в корзину!',
        'quantity': quantity
    })


def remove_from_cart(request, item_id):
    logger.debug(f"Initiating remove_from_cart view for item_id: {item_id}")

    if request.user.is_authenticated:
        # Проверяем, есть ли такой товар в корзине пользователя
        try:
            cart_item = CartItem.objects.filter(product_id=item_id, cart__user=request.user).first()
            if cart_item:
                cart_item.delete()
                logger.debug(f"Removed product '{cart_item.product.name}' from user '{request.user.username}' cart.")
            else:
                logger.warning(f"Product with ID {item_id} not found in user '{request.user.username}' cart.")
        except CartItem.DoesNotExist:
            logger.warning(f"CartItem with product_id {item_id} does not exist for user '{request.user.username}'.")
    else:
        # Удаление товара из корзины сессии
        cart = request.session.get('cart', {})
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart
            logger.debug(f"Removed product with ID {item_id} from guest cart.")
        else:
            logger.warning(f"Product with ID {item_id} not found in guest cart.")

    logger.debug("Redirecting to cart view after removing item.")
    return redirect('cart')


# Обновление количества товара в Корзине
@csrf_exempt
def update_cart_quantity(request):
    logger.debug("Initiating update_cart_quantity view.")

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        change = request.POST.get('change')

        logger.debug(f"Updating quantity for product_id: {product_id} with change: {change}")

        if not product_id or not change:
            logger.warning("Update cart quantity failed: Invalid request parameters.")
            return JsonResponse({'success': False, 'error': 'Invalid request'})

        try:
            change = int(change)
            if request.user.is_authenticated:
                # Для зарегистрированных пользователей
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item = cart.items.get(product_id=product_id)
                old_quantity = cart_item.quantity
                cart_item.quantity = max(1, cart_item.quantity + change)
                cart_item.save()
                logger.debug(
                    f"Updated cart item quantity for product_id {product_id} from {old_quantity} to {cart_item.quantity} for user '{request.user.username}'."
                )
                total_price = float(cart.total_price())  # Преобразуем в float-формат
                logger.debug(f"New total price for user '{request.user.username}': ${total_price}")
            else:
                # Для гостей
                cart_session = request.session.get('cart', {})
                if product_id in cart_session:
                    old_quantity = cart_session[product_id]['quantity']
                    cart_session[product_id]['quantity'] = max(1, cart_session[product_id]['quantity'] + change)
                    request.session['cart'] = cart_session
                    request.session.modified = True
                    logger.debug(
                        f"Updated cart item quantity for product_id {product_id} from {old_quantity} to {cart_session[product_id]['quantity']} for guest."
                    )
                    total_price = sum(float(item['price']) * item['quantity'] for item in cart_session.values())
                    logger.debug(f"New total price for guest: ${total_price}")
                else:
                    logger.warning(f"Product with ID {product_id} not found in guest cart.")
                    return JsonResponse({'success': False, 'error': 'Product not found in cart'})

            return JsonResponse({'success': True, 'total_price': total_price})
        except Exception as e:
            logger.error(f"Error updating cart quantity: {e}")
            return JsonResponse({'success': False, 'error': str(e)})

    logger.warning("Update cart quantity failed: Invalid request method.")
    return JsonResponse({'success': False, 'error': 'Invalid request'})

def toggle_favorite(request, product_id):
    """
    Добавляет или удаляет товар из избранного, хранящегося в сессии.
    Работает и для гостей, и для авторизованных пользователей.

    """
    logger.debug("Initiating toggle_favorite view with product_id=%s", product_id)

    if request.method == 'POST':
        try:
            # Приводим product_id к int, чтобы в favorites хранились именно числа
            product_id = int(product_id)
        except ValueError:
            logger.warning("Invalid product_id '%s' (not an integer).", product_id)
            return JsonResponse({'error': 'Invalid product_id'}, status=400)

        # Получаем текущий список избранного из сессии
        favorites = request.session.get('favorites', [])

        # Проверяем, есть ли product_id в списке
        if product_id in favorites:
            favorites.remove(product_id)
            request.session['favorites'] = favorites
            request.session.modified = True

            logger.debug("Product %d removed from favorites.", product_id)
            # Возвращаем также текущее кол-во избранных
            return JsonResponse({
                'status': 'removed',
                'product_id': product_id,
                'favorites_count': len(favorites),
            })
        else:
            favorites.append(product_id)
            request.session['favorites'] = favorites
            request.session.modified = True

            logger.debug("Product %d added to favorites.", product_id)
            # Возвращаем также текущее кол-во избранных
            return JsonResponse({
                'status': 'added',
                'product_id': product_id,
                'favorites_count': len(favorites),
            })

    else:
        logger.warning("toggle_favorite called with invalid method: %s", request.method)
        return JsonResponse({'error': 'Invalid HTTP method'}, status=405)

# Личныый кабинет
@login_required
def personal_cabinet(request):
    # Получение имени покупателя
    customer_name = request.user.first_name or request.user.last_name or request.user.username

    # Получение заказов текущего пользователя, сортировка по дате (от новых к старым)
    user_orders = request.user.orders.prefetch_related('items__product', 'delivery').order_by('-created_at')

    # Подсчет сумм для различных статусов с учетом иерархии статусов
    total_paid = user_orders.filter(status__in=['paid', 'completed']).aggregate(total=Sum('total_price'))['total'] or 0
    total_completed = user_orders.filter(status='completed').aggregate(total=Sum('total_price'))['total'] or 0
    total_all = user_orders.aggregate(total=Sum('total_price'))['total'] or 0

    context = {
        'customer_name': customer_name,
        'user_orders': user_orders,
        'total_paid': total_paid,
        'total_completed': total_completed,
        'total_all': total_all,
    }
    return render(request, 'orders/personal_cabinet.html', context)

# О Компании
def about(request):
    logger.debug("Initiating about view.")

    best_sellers = BestSeller.objects.filter(is_featured=True)
    logger.debug(f"Retrieved {best_sellers.count()} featured best sellers for about page.")

    team_members = TeamMember.objects.all()
    logger.debug(f"Retrieved {team_members.count()} team members for about page.")

    testimonials = Testimonial.objects.all()
    logger.debug(f"Retrieved {testimonials.count()} testimonials for about page.")

    context = {
        'best_sellers': best_sellers,
        'team_members': team_members,
        'testimonials': testimonials,
    }

    logger.debug("Rendering about.html with context.")
    return render(request, 'orders/about.html', context)


def get_footer_context():
    logger.debug("Retrieving footer context.")

    # Получение всех коллекций
    collections = Collection.objects.all()
    logger.debug(f"Retrieved {collections.count()} collections for footer.")

    # Получение всех категорий
    categories = Category.objects.all()
    logger.debug(f"Retrieved {categories.count()} categories for footer.")

    return {
        'collections': collections,
        'categories': categories,
    }


# для Footer
def shop_by_collection(request, slug):
    logger.debug(f"Initiating shop_by_collection view for slug: {slug}")

    collection = get_object_or_404(Collection, slug=slug)
    logger.debug(f"Retrieved collection: {collection.name}")

    products = Product.objects.filter(collection=collection)
    logger.debug(f"Retrieved {products.count()} products in collection '{collection.name}'.")

    context = {
        'collection': collection,
        'products': products,
    }
    logger.debug("Rendering collections.html with context.")
    return render(request, 'orders/collections.html', context)


def shop_by_category(request, slug):
    """
    Отображает страницу shop.html, фильтруя товары по конкретной категории (slug).
    Также передаёт аннотированные категории, чтобы в шаблоне можно было
    использовать category.product_count.
    """
    logger.debug(f"Initiating shop_by_category view for slug: {slug}")

    # Получаем объект категории по slug или 404
    category = get_object_or_404(Category, slug=slug)
    logger.debug(f"Retrieved category: {category.name}")

    # Фильтруем товары только этой категории
    products = Product.objects.filter(category=category)
    logger.debug(f"Retrieved {products.count()} products in category '{category.name}'.")

    # Аннотируем все категории, чтобы иметь category.product_count
    categories_annotated = Category.objects.annotate(product_count=Count('products'))
    logger.debug(f"Annotated categories with product_count. Total categories: {categories_annotated.count()}")

    # Формируем контекст для шаблона
    context = {
        'category': category,               # Текущая категория
        'products': products,               # Товары этой категории
        'categories_annotated': categories_annotated,  # Все категории с подсчитанным product_count
    }
    logger.debug("Rendering shop.html with context.")
    return render(request, 'orders/shop.html', context)
