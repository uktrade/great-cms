import re

from django import template

from core import cms_slugs

register = template.Library()


@register.simple_tag()
def url_map(key):
    url_mapping = {
        'DASHBOARD': cms_slugs.DASHBOARD_URL,
        'PRIVACY': cms_slugs.PRIVACY_NOTICE_URL,
        'TERMS': cms_slugs.TERMS_URL,
        'EXPORTPLAN_DASHBOARD': cms_slugs.EXPORT_PLAN_DASHBOARD_URL,
    }

    return url_mapping.get(key.upper())


@register.simple_tag(takes_context=True)
def path_match(context, match):
    # match the current path with provided regexp
    request = context.get('request')
    if request:
        path = request.path
        return re.search(match, path)
