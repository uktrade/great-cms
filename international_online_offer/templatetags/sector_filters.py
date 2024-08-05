from django import template

register = template.Library()


@register.filter
def get_sector_display(value):
    if '_' not in value:
        return value

    return value.replace('_', ' ').capitalize()
