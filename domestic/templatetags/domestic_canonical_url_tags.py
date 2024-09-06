from django import template

from core.utils import derive_canonical_url, hreflang_and_x_default_link

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
def hreflang_tags(context):
    request = context['request']
    canonical_url = derive_canonical_url(request)
    absolute_url = request.get_full_path()
    if canonical_url == absolute_url:
        if 'microsite' in canonical_url:
            canonical_url.replace('microsite', 'campaign-site')
        return hreflang_and_x_default_link(canonical_url, 'en-gb')
    return ''
