from django import template

register = template.Library()


@register.filter
def get_item(dict, key):
    if hasattr(dict, 'get'):
        return dict.get(key.lower())
    return ''
