from django import template
from core import constants

register = template.Library()


@register.simple_tag()
def url_map(key):
    url_mapping = {
        'DASHBOARD': constants.DASHBOARD_URL
    }

    return url_mapping.get(key.upper())
