from django import template

register = template.Library()


@register.filter
def get_item(dict, key):
    if hasattr(dict, 'get'):
        if isinstance(key, int):
            return dict.get(key)
        return dict.get(key)
    return ''
