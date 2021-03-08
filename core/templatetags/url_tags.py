# Templatetags related to URL manipulation

from html import unescape
from urllib.parse import unquote, unquote_plus

from django import template
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse

from core import cms_slugs

register = template.Library()


@register.simple_tag
def get_intended_destination(
    request,
    default_destination=cms_slugs.DASHBOARD_URL,
):
    """For the given request, which should have been redirected
    to a login / sign up view, extract a relative path to use as an
    onward destination after an intermediate process (eg login/signup)
    has been completed -- ie 'where did ?next= want to go and does
    it make sense?'

    If a referring URL is not a local path, or is in a skip-list, just
    return the default post-authentication destination
    """
    skip_list = [
        # List of full URL paths (not just starts of paths)
        # which mean we redirect to default_destination after
        # login instead
        '/',
        reverse('core:login'),
        reverse('core:signup'),
    ]
    proto_delimiter = '://'
    intended_destination = request.GET.get(REDIRECT_FIELD_NAME, '')

    if not intended_destination or any(
        [
            intended_destination[0] != '/',  # ie, not a relative url
            # a path we don't want to send people to after login
            intended_destination in skip_list,
            unquote(intended_destination) in skip_list,
            unquote_plus(intended_destination) in skip_list,
            unescape(intended_destination) in skip_list,
            # eg an ongoing querystring contains a full url:
            proto_delimiter in unquote(intended_destination),
            proto_delimiter in unquote_plus(intended_destination),
            proto_delimiter in unescape(intended_destination),
        ]
    ):
        return default_destination

    return intended_destination
