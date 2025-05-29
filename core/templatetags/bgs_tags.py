from django import template
from django.conf import settings

from core.helpers import is_bgs_site as bgs_site

register = template.Library()


@register.simple_tag
def is_bgs_site(root_url):
    return bgs_site(root_url)


@register.filter
def is_bgs_host(request_host):
    """
    Template filter to check if the given host is a BGS site
    """
    return settings.BGS_SITE in request_host
