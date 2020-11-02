from django import template
from core import cms_slugs
import re

register = template.Library()


@register.simple_tag()
def url_map(key):
    url_mapping = {
        'DASHBOARD': cms_slugs.DASHBOARD_URL,
        'c': cms_slugs.PRIVACY_NOTICE_URL,
        'TERMS': cms_slugs.TERMS_URL,
    }

    return url_mapping.get(key.upper())


@register.simple_tag(takes_context=True)
def path_match(context, match):
    # match the current path with provided regexp
    request = context.get('request')
    path = request.path
    return re.search(match, path)
