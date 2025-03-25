from django import template

from core.helpers import is_bgs_site as bgs_site

register = template.Library()


@register.simple_tag
def is_bgs_site(path):
    return bgs_site(path)
