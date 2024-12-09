from django import template

register = template.Library()

@register.filter
def range(value):
    """Возвращает диапазон от 0 до value."""
    try:
        return range(int(value))
    except (ValueError, TypeError):
        return []
