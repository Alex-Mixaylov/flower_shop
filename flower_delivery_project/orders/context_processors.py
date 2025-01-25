from .models import Category
from orders.models import Cart
from django.db.models import Count

import logging


# Контекстный процессор для добавления переменных во все шаблоны, а именно в меню

logger = logging.getLogger(__name__)

def category_context(request):
    categories = Category.objects.annotate(product_count=Count('products'))
    logger.debug("Rendering index.html with context.")
    logger.debug(categories)  # Вывод QuerySet в лог
    for category in categories:
        logger.debug(f"Category: {category.name}, Product Count: {category.product_count}")
    return {'categories': categories}


def cart_items_processor(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return {'cart_items': cart.items.all()}
    return {'cart_items': []}

def favorites_count_processor(request):

    # Если нет 'favorites' в сессии — вернём 0
    favorites = request.session.get('favorites')
    if not favorites:
        return {'favorites_count': 0}
    # Если есть, считаем их кол-во
    return {'favorites_count': len(favorites)}