from .models import Category
from orders.models import Cart

def category_context(request):
    """
    Контекстный процессор для добавления категорий во все шаблоны.
    """
    categories = Category.objects.all()
    return {
        'categories': categories,
    }

def cart_items_processor(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return {'cart_items': cart.items.all()}
    return {'cart_items': []}
