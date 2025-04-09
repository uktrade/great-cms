from django import template

from core.helpers import is_bgs_site as bgs_site

register = template.Library()


@register.simple_tag
def is_bgs_site(root_url):
    return bgs_site(root_url)
