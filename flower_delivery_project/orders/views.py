from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import User, Product, FlowerType, FlowerColor, Category, BestSeller, TeamMember, Testimonial, Review, Collection, Slide, ComboOffer, Cart, CartItem
from .forms import ReviewForm

from django.db.models import F

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required

from django.db.models import Count
from django.db.models import Avg

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect

import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


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

# Регистрация нового пользователя
@csrf_exempt
def register(request):
    if request.method == 'POST':
        fullname = request.POST.get('fullname', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
        confirmpassword = request.POST.get('confirmpassword', '').strip()

        # Проверка заполненности полей
        if not fullname or not email or not password or not confirmpassword:
            return JsonResponse({'success': False, 'error': 'All fields are required.'})

        # Проверка совпадения паролей
        if password != confirmpassword:
            return JsonResponse({'success': False, 'error': 'Passwords do not match.'})

        # Проверка существующего пользователя
        if User.objects.filter(username=fullname).exists():
            return JsonResponse({'success': False, 'error': 'Username already exists.'})

        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'error': 'Email is already registered.'})

        # Создание пользователя
        user = User.objects.create_user(username=fullname, email=email, password=password)
        user.save()

        return JsonResponse({'success': True, 'message': 'Registration successful! Please log in.'})

    return JsonResponse({'success': False, 'error': 'Invalid request method.'})


# Страница товара
def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.filter(is_approved=True)  # Показываем только одобренные отзывы

    # Обработка формы отзыва
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Вы должны войти в систему, чтобы оставить отзыв.')
            return redirect('custom_login')  # Изменяем редирект на кастомную страницу логина

        form = ReviewForm(request.POST)
        if form.is_valid():
            if not Review.objects.filter(product=product, author=request.user).exists():
                review = form.save(commit=False)
                review.product = product  # Привязываем отзыв к текущему продукту
                review.author = request.user
                review.save()
                messages.success(request, 'Ваш отзыв отправлен и ожидает модерации.')
            else:
                messages.error(request, 'Вы уже оставили отзыв для этого товара.')
        else:
            messages.error(request, 'Ошибка при отправке отзыва. Пожалуйста, попробуйте еще раз.')

    else:
        form = ReviewForm()

    return render(request, 'orders/product-details.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
    })

# Каталог на сайте
def shop(request):
    # Получение всех фильтров
    category_ids = request.GET.getlist('categories')  # Список ID категорий
    min_price = request.GET.get('min_price')  # Минимальная цена
    max_price = request.GET.get('max_price')  # Максимальная цена
    flower_type_ids = request.GET.getlist('flower_types')  # Список ID типов цветов
    flower_color_ids = request.GET.getlist('flower_colors')  # Список ID цветов цветов

    # Базовый QuerySet для всех продуктов
    products_list = Product.objects.all().order_by('id')  # Добавляем сортировку по ID для пагинации

    # Фильтрация по категориям
    if category_ids:
        products_list = products_list.filter(category__id__in=category_ids)

    # Фильтрация по ценовому диапазону
    if min_price and max_price:
        products_list = products_list.filter(price__gte=min_price, price__lte=max_price)

    # Фильтрация по типу цветов
    if flower_type_ids:
        products_list = products_list.filter(flower_types__id__in=flower_type_ids)

    # Фильтрация по цвету цветов
    if flower_color_ids:
        products_list = products_list.filter(flower_colors__id__in=flower_color_ids)

    # Удаление дублирующихся продуктов (если фильтры приводят к повторным объектам)
    products_list = products_list.distinct()

    # Пагинация
    paginator = Paginator(products_list, 9)  # По 9 товаров на страницу
    page_number = request.GET.get('page')

    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        products = paginator.page(1)  # Если номер страницы не число, показать первую страницу
    except EmptyPage:
        products = paginator.page(paginator.num_pages)  # Если страница пуста, показать последнюю страницу

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
    }
    print(products)  # Вывод списка продуктов
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

def cart_view(request):
    cart_items = []
    total_price = 0

    if request.user.is_authenticated:
        # Получение корзины пользователя
        cart, created = Cart.objects.get_or_create(user=request.user)
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
            print(f"Cart Item ID: {item.id}, Product: {item.product}, Price: {item.product.price}, Size: {size_option.size if size_option else 'N/A'}")
            total_price += item.total_price()
    else:
        # Для гостей
        cart_session = request.session.get('cart', {})
        for product_id, product_data in cart_session.items():
            product = Product.objects.get(id=product_id)
            size_option = product.size_option
            subtotal = float(product_data['price']) * product_data['quantity']
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
            print(f"Guest Cart Item ID: {product_id}, Product: {product.name}, Size: {size_option.size if size_option else 'N/A'}")

    # Отладочный вывод
    print(f"Total Price: {total_price}")

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'orders/cart.html', context)

def add_to_cart(request, product_id):
    """
    Функция добавления товара в корзину.
    Работает как для зарегистрированных пользователей, так и для гостей.
    Учитывает количество товара, переданное в POST-запросе.
    """
    product = get_object_or_404(Product, id=product_id)

    # Получаем количество товара из POST-запроса (по умолчанию 1, если не передано)
    quantity = int(request.POST.get('quantity', 1))

    if request.user.is_authenticated:
        # Корзина для зарегистрированных пользователей
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Проверяем, есть ли уже этот товар в корзине
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}  # Используем переданное количество для нового товара
        )

        if not created:
            # Если товар уже есть в корзине, увеличиваем количество
            cart_item.quantity += quantity
            cart_item.save()
            print(f"Обновлено количество товара в корзине для пользователя {request.user}: {cart_item.quantity} шт.")
        else:
            print(f"Добавлен новый товар в корзину для пользователя {request.user}: {quantity} шт.")

    else:
        # Корзина для гостей
        cart = request.session.get('cart', {})

        if str(product_id) in cart:
            # Если товар уже есть в корзине, увеличиваем количество
            cart[str(product_id)]['quantity'] += quantity
            print(f"Обновлено количество товара в корзине для гостя: {cart[str(product_id)]['quantity']} шт.")
        else:
            # Если товара нет в корзине, добавляем его с указанным количеством
            cart[str(product_id)] = {
                'quantity': quantity,
                'name': product.name,
                'price': round(float(product.price), 2),
                'old_price': round(float(product.old_price), 2) if product.old_price else None,
                'image_main': product.image_main.url if product.image_main else None,
            }
            print(f"Добавлен новый товар в корзину для гостя: {quantity} шт.")

        # Сохраняем корзину в сессию
        request.session['cart'] = cart

    # Отправляем JSON-ответ с подтверждением добавления товара и его количеством
    return JsonResponse({
        'message': 'Товар успешно добавлен в корзину!',
        'quantity': quantity
    })

def remove_from_cart(request, item_id):
    if request.user.is_authenticated:
        # Проверяем, есть ли такой товар в корзине пользователя
        try:
            cart_item = CartItem.objects.filter(product_id=item_id, cart__user=request.user).first()
            if cart_item:
                cart_item.delete()
        except CartItem.DoesNotExist:
            pass
    else:
        # Удаление товара из корзины сессии
        cart = request.session.get('cart', {})
        if str(item_id) in cart:
            del cart[str(item_id)]
            request.session['cart'] = cart

    return redirect('cart')

# Обновление кол-ва товара в Корзине
#@csrf_protect

logger = logging.getLogger(__name__)

@csrf_exempt
def update_cart_quantity(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        change = request.POST.get('change')

        if not product_id or not change:
            return JsonResponse({'success': False, 'error': 'Invalid request'})

        try:
            if request.user.is_authenticated:
                # Для зарегистрированных пользователей
                cart, created = Cart.objects.get_or_create(user=request.user)
                cart_item = cart.items.get(product_id=product_id)
                cart_item.quantity = max(1, cart_item.quantity + int(change))
                cart_item.save()
                total_price = float(cart.total_price())  # Преобразуем в float-формат
            else:
                # Для гостей
                cart_session = request.session.get('cart', {})
                if product_id in cart_session:
                    cart_session[product_id]['quantity'] = max(1, cart_session[product_id]['quantity'] + int(change))
                    request.session['cart'] = cart_session
                    request.session.modified = True
                    total_price = sum(float(item['price']) * item['quantity'] for item in cart_session.values())

            return JsonResponse({'success': True, 'total_price': total_price})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request'})


# О Компании
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
