from django.core.mail import send_mail
from django.shortcuts import render, redirect

from django.conf import settings

def index(request):
    # Рендеринг HTML-шаблона index.html
    return render(request, 'orders/index.html')

def product_details(request):
    # Рендеринг HTML-шаблона product-details.html
    return render(request, 'orders/product-details.html')

def shop(request):
    # Рендеринг HTML-шаблона shop.html
    return render(request, 'orders/shop.html')

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

#