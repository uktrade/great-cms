from django import template

from core.utils import derive_canonical_url, hreflang_and_x_default_link

register = template.Library()


@register.simple_tag(takes_context=True)
def get_canonical_url(context):
    request = context['request']
    return derive_canonical_url(request)


@register.simple_tag(takes_context=True)
def hreflang_tags(context):
    canonical_url = get_canonical_url(context)
    request = context['request']
    absolute_url = request.get_absolute_url()
    if absolute_url == canonical_url:
        return hreflang_and_x_default_link(canonical_url, 'en')
    return ''
