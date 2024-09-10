from django import template

from core.utils import derive_canonical_url, get_hreflang_tags as get_seo_tags

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
    """
    Only display hreflang and x-default links if absolute url (ie the full path)
    is equal to the canonical url
    essentially if the request url has no parameter
    """
    if 'request' not in context:
        return ''
    canonical_url = get_canonical_url(context)
    return get_seo_tags(context, canonical_url, lang='en-gb')
