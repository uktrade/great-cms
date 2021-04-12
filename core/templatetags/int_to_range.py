from django import template

register = template.Library()


@register.filter(name='int_to_range')
def int_to_range(number):
    return range(number)
