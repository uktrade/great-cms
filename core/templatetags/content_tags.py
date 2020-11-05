import logging
import math
from django import template
from django.utils.http import urlencode
import datetime

from urllib.parse import urlparse

from core.constants import BACKLINK_QUERYSTRING_NAME, LESSON_BLOCK
from core.models import CuratedListPage, DetailPage


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
        backlink = urlencode(query={BACKLINK_QUERYSTRING_NAME: request.get_full_path()})

        delimiter = '?'
        parsed_outbound_url = urlparse(outbound_url)
        if parsed_outbound_url.query:
            # ie the outbound URL has a querystring so we need to ADD our backlink to it
            delimiter = '&'
        outbound_url += f'{delimiter}{backlink}'

    return outbound_url


@register.simple_tag
def get_topic_title_for_lesson(detail_page: DetailPage) -> str:
    """For the given lesson, find the topic it belongs to and return that topic's title"""

    # Get the module this page belongs to, if we can
    clp = CuratedListPage.objects.live().ancestor_of(detail_page).first()
    if not clp:
        return ''

    # Find the topic this detailpage is referenced in
    for topic_block in clp.specific.topics:
        for lesson_or_placeholder in topic_block.value.get('lessons_and_placeholders', []):
            if lesson_or_placeholder.block_type == LESSON_BLOCK:
                if lesson_or_placeholder.value == detail_page:
                    return topic_block.value.get('title')

    return ''


@register.simple_tag
def get_lesson_progress_for_topic(lesson_completion_data, lessons_and_placeholders) -> dict:
    # Computes simple stats from the data structures passed in, doing a light safety check along the way
    lesson_ids = [
        x.value.id for x in lessons_and_placeholders
        if x.block_type == LESSON_BLOCK
    ]

    # Watch out for zany data, such as more items completed than currently available
    if lesson_completion_data and not lesson_completion_data.issubset(set(lesson_ids)):
        return {}

    lessons_completed = len(lesson_completion_data) if lesson_completion_data else 0
    lessons_available = len(lesson_ids)

    return {
        'lessons_completed': lessons_completed,
        'lessons_available': lessons_available
    }
