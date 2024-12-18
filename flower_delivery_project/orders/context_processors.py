from .models import Category

def category_context(request):
    """
    Контекстный процессор для добавления категорий во все шаблоны.
    """
    categories = Category.objects.all()
    return {
        'categories': categories,
    }
