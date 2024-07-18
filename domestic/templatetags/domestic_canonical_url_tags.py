from django import template

from core.utils import derive_canonical_url

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
