import logging
import math
from django import template
from django.utils.http import urlencode
import datetime

from core.constants import BACKLINK_QUERYSTRING_NAME

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
def format_timedelta(timedelta, pluralize=False):

    if isinstance(timedelta, datetime.timedelta):
        # round up to next minute
        rounded_mins = math.ceil(timedelta.total_seconds() / 60)
        hours, mins = divmod(rounded_mins, 60)
        hours_plural = 's' if hours > 1 and pluralize else ''
        mins_plural = 's' if mins > 1 and pluralize else ''
        hours_str = f'{hours} hour{hours_plural}' if hours else ''
        mins_str = f'{mins} min{mins_plural}' if mins or not hours else ''
        return f'{hours_str} {mins_str}'.strip()
    return ''


@register.simple_tag()
def pluralize(value, plural_string='s'):
    return plural_string if value != 1 else ''


@register.simple_tag(takes_context=True)
def get_backlinked_url(context, outbound_url):
    """Appends a querystring to the provided outbound_url that features the
    current page's relative path as an encoded string.

    Use case is allowing pages to link to others and tell them, in a robust way,
    where to take the user back to (eg export plan -> lesson -> export plan)
    """

    request = context.get('request')
    if request:
        backlink = urlencode(query={BACKLINK_QUERYSTRING_NAME: request.path})
        if request.GET:
            delimiter = '&'
        else:
            delimiter = '?'
        outbound_url += f'{delimiter}{backlink}'

    return outbound_url
