import calendar
import datetime
import logging
import math
import re
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from django import template
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from core.constants import BACKLINK_QUERYSTRING_NAME
from core.helpers import millify
from core.models import DetailPage, TopicPage

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


@register.filter
def str_to_datetime(datestr):
    return parse_datetime(datestr)


@register.filter
def month_name(month_number):
    if month_number:
        return calendar.month_name[month_number]
    return ''


@register.simple_tag()
def pluralize(value, plural_string='s'):
    return plural_string if value != 1 else ''


@register.filter
def concat(arg1, arg2):
    return str(arg1) + str(arg2)


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
def get_category_title_for_lesson(detail_page: DetailPage) -> str:
    """For the given lesson, find the category it belongs to and
    return that category's title"""
    return detail_page.get_parent().get_parent().title


@register.simple_tag
def get_lesson_progress_for_topic(
    completed_lessons: set,
    topic_id: int,
) -> dict:
    # Computes simple stats from the data structures passed in, doing a light safety check along the way

    topic_page = TopicPage.objects.live().specific().filter(id=topic_id).first()

    lesson_ids = DetailPage.objects.live().specific().descendant_of(topic_page).values_list('id', flat=True)

    # Watch out for zany data, such as more items completed than currently available
    if completed_lessons and not completed_lessons.issubset(set(lesson_ids)):
        return {}

    lessons_completed = len(completed_lessons) if completed_lessons else 0
    lessons_available = len(lesson_ids)

    return {'lessons_completed': lessons_completed, 'lessons_available': lessons_available}


@register.filter
def is_lesson_page(page):
    return isinstance(page.specific, DetailPage)


@register.filter(name='multiply_by_exponent', is_safe=False)
def multiply_by_exponent(val, exponent=3, base=10):
    """
    Simple template tag that takes an integer and returns new integer of base ** exponent

    Return
        int

    Params:
        val: int
            The integer to be multiplied
        exponent: int
            The exponent
        base: int
            The base
    """

    if type(val) is int:
        int_val = int(val)
    else:
        int_val = 0

    return int_val * (base**exponent)


@register.filter(name='friendly_number', is_safe=False)
def friendly_number(val):
    """
    Convert numbers to a friendly format e.g: 1 thousand, 123.4 thousand, 1.11 million, 111.42 million.
    Return
        str
            e.g: 1.02 thousand, 123.43 thousand, 111.42 million, 1.14 billion
    Params:
        val: int
            The input value
    """

    if type(val) is int:
        int_val = int(val)
    else:
        int_val = 0

    return millify(int_val)


@register.simple_tag
def round_to_unit(number, unit, precision=1):
    units = {'thousand': 1e3, 'million': 1e6, 'billion': 1e9, 'trillion': 1e12}

    if unit and unit in units:
        number = number / units[unit]

    return f'{number:.{precision}f}'


@register.simple_tag
def reference_period(data, capitalise=False):
    output = ''

    if data['resolution'] == 'month' and 1 <= data['period'] <= 12:
        month = month_name(data['period'])
        year = data['year']
        output = f'twelve months to the end of {month} {year}'

    if data['resolution'] == 'quarter' and 1 <= data['period'] <= 4:
        quarter = data['period']
        year = data['year']
        output = f'four quarters to the end of Q{quarter} {year}'

    if capitalise:
        return output[0].upper() + output[1:]

    return output


@register.filter
def get_css_class_from_string(string):
    return string.replace(',', '').replace(' ', '-').lower()


def wrap_tag_in_div(soup, tag_name, wrapper_class):
    for element in soup.findAll(tag_name['tag']):
        div = soup.new_tag('div', **{'class': wrapper_class})
        element.wrap(div)


def add_anchor_classes(soup, class_name):
    header_tags = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    for header_tag in header_tags:
        a_tags = header_tag.find_all('a', href=True)
        for a_tag in a_tags:
            if a_tag['href'].startswith('#'):
                a_tag.attrs['class'] = [class_name]


@register.filter
def add_govuk_classes(value):
    soup = BeautifulSoup(value, 'html.parser')
    mapping = [
        ({'tag': 'h1'}, 'govuk-heading-xl'),
        ({'tag': 'h2'}, 'govuk-heading-l'),
        ({'tag': 'h3'}, 'govuk-heading-m great-font-size-28'),
        ({'tag': 'h4'}, 'govuk-heading-s'),
        ({'tag': 'h5'}, 'govuk-heading-xs'),
        ({'tag': 'h6'}, 'govuk-heading-xs'),
        ({'tag': 'ul'}, 'govuk-list govuk-list--bullet'),
        ({'tag': 'ol'}, 'govuk-list govuk-list--number'),
        ({'tag': 'p'}, 'govuk-body'),
        ({'tag': 'a'}, 'govuk-link'),
        ({'tag': 'div', 'class': 'form-group'}, 'govuk-form-group'),
        ({'tag': 'select', 'class': 'form-control'}, 'govuk-form-control'),
        ({'tag': 'input', 'class': 'form-control'}, 'govuk-form-control'),
        ({'tag': 'label', 'class': 'form-label'}, 'govuk-form-label'),
        ({'tag': 'div', 'class': 'form-group-error'}, 'govuk-form-group-error'),
        ({'tag': 'iframe', 'wrap': True}, 'great-video-embed-16-9'),
        ({'tag': 'a', 'header_parent': True}, 'great-anchor-link'),  # New mapping for <a> tags inside headers
    ]

    for tag_name, class_name in mapping:
        if 'wrap' in tag_name:
            wrap_tag_in_div(soup, tag_name, class_name)
        elif 'class' in tag_name:
            for element in soup.find_all(tag_name['tag'], {'class': tag_name['class']}):
                element.attrs['class'] = [
                    class_name if classname == tag_name['class'] else classname for classname in element.attrs['class']
                ]
        elif 'header_parent' in tag_name:
            add_anchor_classes(soup, class_name)
        else:
            for element in soup.findAll(tag_name['tag']):
                element.attrs['class'] = class_name

    return mark_safe(str(soup))


@register.filter
def get_link_blocks(list_of_blocks):
    return [block for block in list_of_blocks if block.block_type == 'link_block']


@register.filter
def get_text_blocks(list_of_blocks):
    return [block for block in list_of_blocks if block.block_type == 'text']


@register.filter
def get_topic_blocks(list_of_blocks, topic):
    index_of_topic = 0
    result = []

    for parent_index, parent_block in enumerate(list_of_blocks):
        for block in parent_block.value:
            if block.block_type == 'title' and block.value == topic:
                index_of_topic = parent_index

    for index, block in enumerate(list_of_blocks):
        if index == index_of_topic:
            result = [block]

    return result


@register.simple_tag
def get_template_translation_enabled():
    return getattr(settings, 'FEATURE_MICROSITE_ENABLE_TEMPLATE_TRANSLATION', False)


@register.simple_tag
def get_digital_entry_point_enabled():
    return getattr(settings, 'FEATURE_DIGITAL_POINT_OF_ENTRY', False)


@register.filter
def replace_emphasis_tags(content):
    replacements = {'i': 'em', 'b': 'strong'}
    soup = BeautifulSoup(content, 'html.parser')

    for p_tag in soup.find_all('p', class_='govuk-body'):
        for tag, replacement in replacements.items():
            for found_tag in p_tag.find_all(tag):
                found_tag.name = replacement

    return format_html(str(soup))


@register.filter
def make_bold(text):
    return mark_safe(f'<span class="govuk-!-font-weight-bold">{text}</span>')


@register.filter
def highlighted_text(elems):
    s = ''

    if isinstance(elems, str):
        return mark_safe(f'<span class="great-highlighted-text">{elems}</span>')
    elif isinstance(elems, list):
        for index, item in enumerate(elems):
            text = f'<span class="great-highlighted-text">{item}</span>'

            if len(elems) == 1 or index == 0:
                s += text
            elif index != len(elems) - 1:
                s += ', ' + text
            else:
                s += ' and ' + text

        return mark_safe(s)
    else:
        return s


@register.filter
def tag_text_mapper(text):
    if text == 'howTo':
        return 'How to'
    if text == 'govuk':
        return 'GOV.UK'

    return text


@register.filter
def url_type(url):
    if re.search('great', url):
        return 'internal'
    else:
        return 'external'
