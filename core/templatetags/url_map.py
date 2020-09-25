from django import template
from core import constants
import re

register = template.Library()


@register.simple_tag()
def url_map(key):
    url_mapping = {
        'DASHBOARD': constants.DASHBOARD_URL
    }

    return url_mapping.get(key.upper())


@register.simple_tag(takes_context=True)
def path_match(context, match):
    # match the current path with provided regexp
    request = context.get('request')
    path = request.path
    return re.search(match, path)
