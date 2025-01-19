from django import template

register = template.Library()

@register.filter
def range_filter(value):
    """Возвращает диапазон от 0 до value."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return []
@register.filter
def multiply(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def float_subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0.0
@register.filter
def custom_pagination(paginator, current_page):
    """
    Возвращает список страниц для пагинации с учетом текущей страницы.
    """
    page_range = paginator.page_range
    total_pages = paginator.num_pages
    visible_pages = 5  # Количество отображаемых страниц

    if total_pages <= visible_pages:
        return page_range

    start_page = max(current_page - 2, 1)
    end_page = min(current_page + 2, total_pages)

    return range(start_page, end_page + 1)

@register.filter
def star_filter(value):
    """Создаёт диапазон от 0 до value для звёздочек."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return range(0)
