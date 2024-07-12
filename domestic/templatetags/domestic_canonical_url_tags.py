from django import template

from core.utils import derive_canonical_url

register = template.Library()


@register.simple_tag(takes_context=True)
def get_canonical_url(context):
    request = context['request']
    return derive_canonical_url(request)
