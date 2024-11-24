from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse

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
        # Здесь можно обработать данные формы, например, сохранить сообщение в БД
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        print(f"Message from {name} ({email}): {message}")  # Для тестирования
        return HttpResponseRedirect(reverse('thanks'))  # Перенаправление на страницу благодарности
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
# def shop(request):
#     return HttpResponse("<h1>Это Страница магазина - shop.html</h1>")
#
# def product_details(request):
#     return HttpResponse("<h1>Это Страница конкретного товара - product-details.html</h1>")
#
# def thanks(request):
#     return HttpResponse("<h1>Это Страница благодарности за  заказ - thanks.html</h1>")
#
# def cart(request):
#     return HttpResponse("<h1>Это Страница корзина за  заказ - cart.html</h1>")
#
# def checkout(request):
#     return HttpResponse("<h1>Это Страница оформления за  заказ - checkout.html</h1>")
#
# def collections(request):
#     return HttpResponse("<h1>Это Страница Коллекций - collections.html</h1>")
#
# def contact(request):
#     return HttpResponse("<h1>Это Страница Контакты - contact.html</h1>")