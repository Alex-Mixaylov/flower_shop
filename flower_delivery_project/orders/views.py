from django.http import HttpResponse

def index(request):
    return HttpResponse("<h1>Это Главная страница - index.html</h1>")

def shop(request):
    return HttpResponse("<h1>Это Страница магазина - shop.html</h1>")

def product_details(request):
    return HttpResponse("<h1>Это Страница конкретного товара - product-details.html</h1>")

def thanks(request):
    return HttpResponse("<h1>Это Страница благодарности за  заказ - thanks.html</h1>")

def cart(request):
    return HttpResponse("<h1>Это Страница корзина за  заказ - cart.html</h1>")

def checkout(request):
    return HttpResponse("<h1>Это Страница оформления за  заказ - checkout.html</h1>")

def collections(request):
    return HttpResponse("<h1>Это Страница Коллекций - collections.html</h1>")

def contact(request):
    return HttpResponse("<h1>Это Страница Контакты - contact.html</h1>")