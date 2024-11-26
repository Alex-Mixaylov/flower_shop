from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from .models import Product, Category, BestSeller, TeamMember, Testimonial


from django.conf import settings

def index(request):
    # Рендеринг HTML-шаблона index.html
    return render(request, 'orders/index.html')


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
    # Рендеринг HTML-шаблона collections.html
    return render(request, 'orders/collections.html')

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

def cart(request):
    # Рендеринг HTML-шаблона cart.html
    return render(request, 'orders/cart.html')

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