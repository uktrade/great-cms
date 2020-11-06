import logging
import math
from django import template
from django.utils.http import urlencode
import datetime

from urllib.parse import urlparse

from core.constants import BACKLINK_QUERYSTRING_NAME
from core.models import (
    DetailPage,
    LessonPlaceholderPage,
    TopicPage,
)

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
    """For the given lesson, find the topic it belongs to and
    return that topic's title"""
    return detail_page.get_parent().title


@register.simple_tag
def get_lesson_progress_for_topic(
    completed_lessons: set,
    topic_id: int,
) -> dict:
    # Computes simple stats from the data structures passed in, doing a light safety check along the way

    topic_page = TopicPage.objects.live().specific().filter(id=topic_id).first()

    lesson_ids = (
        DetailPage.objects
        .live()
        .specific()
        .descendant_of(topic_page)
        .values_list('id', flat=True)
    )

    # Watch out for zany data, such as more items completed than currently available
    if completed_lessons and not completed_lessons.issubset(set(lesson_ids)):
        return {}

    lessons_completed = len(completed_lessons) if completed_lessons else 0
    lessons_available = len(lesson_ids)

    return {
        'lessons_completed': lessons_completed,
        'lessons_available': lessons_available
    }


@register.filter
def is_lesson_page(page):
    return isinstance(page.specific, DetailPage)


@register.filter
def is_placeholder_page(page):
    return isinstance(page.specific, LessonPlaceholderPage)
