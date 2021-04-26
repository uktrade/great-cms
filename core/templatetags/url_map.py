import re

from django import template

from core import cms_slugs

register = template.Library()


@register.simple_tag()
def url_map(key):
    return getattr(cms_slugs, key.upper())


@register.simple_tag(takes_context=True)
def path_match(context, match):
    # match the current path with provided regexp
    request = context.get('request')
    if request:
        path = request.path
        return re.search(match, path)
