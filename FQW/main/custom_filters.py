from django import template

register = template.Library()

@register.filter
def get_field(form, field_name):
    return form[field_name]

@register.filter(name='intspace')
def intspace(value):
    if value is None:
        return ''
    try:
        # Преобразуем в целое число
        value = int(value)
        # Добавляем пробелы между разрядами
        return f"{value:,}".replace(',', ' ')
    except (ValueError, TypeError):
        return value