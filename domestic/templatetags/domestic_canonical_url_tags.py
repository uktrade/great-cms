from django import template
from django.utils.safestring import mark_safe

from core.utils import (
    derive_absolute_url,
    derive_canonical_url,
    hreflang_and_x_default_link,
)

register = template.Library()


@register.simple_tag(takes_context=True)
def get_canonical_url(context):
    request = context.get('request', None)
    if request:
        if 'microsite' in request.path:
            request.path.replace('microsite', 'campaign-site')
        return derive_canonical_url(request)
    else:
        return ''


@register.simple_tag(takes_context=True)
def get_hreflang_tags(context):
    if 'request' not in context:
        return ''
    request = context['request']
    canonical_url = derive_canonical_url(request)
    if 'microsite' in request.path:
        request.path.replace('microsite', 'campaign-site')
    absolute_url = derive_absolute_url(request)
    if canonical_url == absolute_url:
        return mark_safe(hreflang_and_x_default_link(canonical_url, 'en-gb'))
    return ''
