from django import template
from django.utils.safestring import mark_safe

from core.utils import derive_canonical_url, hreflang_and_x_default_link

register = template.Library()


@register.simple_tag(takes_context=True)
def get_canonical_url(context):
    request = context['request']
    return derive_canonical_url(request)


@register.filter(is_safe=True, takes_context=True)
def get_hreflang_tags(context):
    canonical_url = get_canonical_url(context)
    request = context['request']
    absolute_url = request.get_full_path()
    if absolute_url == canonical_url:
        return mark_safe(hreflang_and_x_default_link(canonical_url, 'en-gb'))
    return None
