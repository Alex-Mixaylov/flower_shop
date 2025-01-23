from .models import Category
from orders.models import Cart


# Контекстный процессор для добавления переменных во все шаблоны, а именно в меню

def category_context(request):

    categories = Category.objects.all()
    return {
        'categories': categories,
    }

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