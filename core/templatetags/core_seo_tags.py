from django import template

from core.utils import derive_absolute_url

register = template.Library()


@register.simple_tag(takes_context=True)
def get_absolute_url(context):
    request = context['request']
    absolute_url = derive_absolute_url(request)
    return absolute_url
