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

@register.filter(name='subtract')
def subtract(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ''
