# myapp/templatetags/my_filters1.py

from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Возвращает значение для заданного ключа"""
    return dictionary.get(key)
