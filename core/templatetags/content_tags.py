import calendar
import datetime
import logging
import math
import re
from typing import Union
from urllib.parse import urlparse, urlsplit

from bs4 import BeautifulSoup
from django import template
from django.conf import settings
from django.utils.dateparse import parse_datetime
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.text import slugify

from core.constants import (
    BACKLINK_QUERYSTRING_NAME,
    CHEG_EXCLUDED_COUNTRY_CODES,
    EU_TRAVEL_ADVICE_URLS,
    META_LABELS,
)
from core.helpers import millify
from core.models import DetailPage, LessonPlaceholderPage, TopicPage
from domestic_growth.constants import (
    CARD_META_DATA,
    DYNAMIC_SNIPPET_NAMES,
    FINANCE_AND_SUPPORT_REGION_MAPPINGS,
    FIND_A_GRANT_MAPPINGS,
    REGION_IMAGES,
    INTERNAL_GREAT_DOMAIN,
    INTERNAL_BUSINESS_DOMAIN,
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


@register.filter
def is_placeholder_page(page):
    return isinstance(page.specific, LessonPlaceholderPage)


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


def add_filter_classes(soup, mapping):
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


GOVUK_CLASSES_MAPPING = [
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


@register.filter
def add_govuk_classes(value):
    soup = BeautifulSoup(value, 'html.parser')
    return add_filter_classes(soup, GOVUK_CLASSES_MAPPING)


@register.filter
def add_card_govuk_classes(value):
    soup = BeautifulSoup(value, 'html.parser')
    mapping = [
        ({'tag': 'p'}, 'govuk-body govuk-!-margin-bottom-9') if item == ({'tag': 'p'}, 'govuk-body') else item
        for item in GOVUK_CLASSES_MAPPING
    ]
    return add_filter_classes(soup, mapping)


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


@register.filter
def is_email(value):
    # Use regular expression to check if the value is an email address
    return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', value)) or value.startswith('mailto:')


@register.filter
def extract_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc


@register.filter
def handle_external_links(html_content, request):
    current_domain = request.get_host()
    soup = BeautifulSoup(html_content, 'html.parser')

    for a_tag in soup.find_all('a'):
        if a_tag.has_attr('href'):
            href = a_tag['href']

            # Check if the URL is an internal link
            if not is_external_link(href, current_domain) or is_email(href):
                continue

            a_tag['target'] = '_blank'

            # Add hidden content after the label
            hidden_content = soup.new_tag('span', attrs={'class': 'great-visually-hidden'})
            hidden_content.string = f'opens {extract_domain(href)} in a new tab'
            a_tag.append(hidden_content)

    return str(soup)


def is_external_link(url, current_domain):
    # Parse the URL
    parsed_url = urlparse(url)

    # Check if the URL has a scheme
    if not parsed_url.scheme:
        return False

    # Check if the URL is not on the current domain
    return parsed_url.netloc != current_domain


@register.filter(name='remove_bold_from_headings')
def remove_bold_from_headings(value):
    heading_pattern = re.compile(r'<(h[1-6])(.*?)><b>(.*?)</b></\1>', re.DOTALL)
    value = heading_pattern.sub(r'<\1\2>\3</\1>', value)
    return value


@register.filter
def get_icon_path(url):
    if url:
        if url.endswith('/'):
            url = url[:-1]
        return 'components/great/includes/' + url.split('/')[-1] + '.svg'
    else:
        return ''


@register.filter
def get_international_icon_path(url):
    url_to_icon_list = (
        ('uk-investment-zones', 'investment-zones'),
        ('uk-tax-and-incentives', 'tax-incentives'),
        ('uk-talent-and-labour', 'talent-labour'),
        ('uk-infrastructure', 'infrastructure'),
        ('clean-growth-in-the-uk', 'clean-growth'),
        ('freeports-in-the-uk', 'freeports'),
        ('uk-innovation', 'innovation'),
        ('sectors', 'sectors'),
    )
    for url_to_icon in url_to_icon_list:
        if url_to_icon[0] in url:
            return 'international/includes/svg/' + url_to_icon[1] + '.svg'
    return ''


@register.simple_tag
def render_automated_list_page_card_content(page, request, module_completion_data):
    if request.user.is_authenticated and module_completion_data:
        completion_percentage = module_completion_data.get('completion_percentage', 0)
        completion_count = module_completion_data.get('completion_count', 0)
        total_pages = module_completion_data.get('total_pages', 0)
        html_content = format_html(
            f"""
            <div class="learn-card-description">
                { page.heading}
            </div>
            <div class="progess-container great-display-flex great-flex-wrap great-flex-column-until-tablet great-gap">
            <div class="learn__category-progress-container">
                <div class="learn__category-progress">
                <span style="width: {completion_percentage}%"></span>
                </div>
                <span class="govuk-label">
                    {completion_count}
                    /
                    {total_pages}
                    marked as complete
                 </span>
                </div>
                </div>
        """
        )
    else:
        html_content = format_html(
            f"""
            <div class="learn-card-description">
            { page.heading}
            </div>
        """
        )
    return html_content


@register.simple_tag
def render_curated_topic_card_content(page, completed_lessons):
    if completed_lessons is None or not hasattr(completed_lessons, '__iter__'):
        completed_lessons = []

    if str(page.id) in map(str, completed_lessons):
        html_content = f"""
            <div class="great-display-flex great-gap-10-30 great-justify-space-between
                  great-flex-column-until-desktop">
                <h3 class="govuk-link great-font-bold govuk-!-margin-0 great-title-link
                     great-card__link great-card__link--underline great-card__link--heading">
                    <span>{page.title}</span>
                </h3>
                <span class="great-badge completed govuk-!-margin-top-2">Completed</span>
            </div>
            """
    else:
        html_content = f"""
            <div class="great-display-flex great-gap-10-30 great-justify-space-between">
                <h3 class="govuk-link great-font-bold govuk-!-margin-0 great-title-link
                     great-card__link great-card__link--underline great-card__link--heading">
                    <span>{page.title}</span>
                </h3>
                <span role="img" class="fa fa-arrow-right govuk-!-margin-right-2 great-text-blue
                     great-font-size-18 great-height-min-content govuk-!-margin-top-1"></span>
            </div>
            """
    return html_content


@register.simple_tag
def get_page_url(page):
    return page.get_full_url()


@register.simple_tag
def show_feedback(page_url):
    return page_url not in ['/login/', '/signup/']


@register.simple_tag
def get_inline_feedback_visibility(page_url):
    result = {
        'show_page_useful': False,
        'show_positive_feedback': False,
        'show_negative_feedback': False,
        'show_detailed_feedback_received': False,
        'show_submission_error': False,
    }

    if 'page_useful=True' in page_url:
        result['show_positive_feedback'] = True
    elif 'page_useful=False' in page_url:
        result['show_negative_feedback'] = True
    elif 'detailed_feedback_submitted=True' in page_url:
        result['show_detailed_feedback_received'] = True
    elif 'submission_error=True' in page_url:
        result['show_submission_error'] = True
    else:
        result['show_page_useful'] = True

    return result


@register.filter
def h3_if(condition, else_heading):
    if condition:
        return 'h3'

    return else_heading


@register.filter
def val_to_int(val: Union[float, int, str]) -> int:
    """
    Utility function that can be called from a django template to return the whole number
    of a decimal. Not to be confused with django's intcomma which retains the fraction part.
    """
    return int(round(float(val)))


@register.filter
def get_category_page_breadcrumbs(page):
    return [
        {'url': '/support/export-support/', 'title': 'Export Support'},
    ]


@register.filter
def get_sub_category_page_breadcrumbs(page, full_page_url):
    parent_category_url = page.get_parent().get_full_url()
    full_page_url = full_page_url.split('?')

    if len(full_page_url) == 2:
        parent_category_url += '?' + full_page_url[1]

    return [
        {'url': '/support/export-support/', 'title': 'Export Support'},
        {'url': parent_category_url, 'title': page.get_parent().specific.page_title},
    ]


@register.filter
def get_meta_tag_label(url):
    if 'great' in url:
        return 'great.gov.uk'

    if 'gov' in url:
        return 'GOV.UK'

    return ''


@register.filter
def get_meta_tag_icon_path(type):
    if 'Service' in type:
        return '/static/icons/hand.svg'

    return '/static/icons/guidance.svg'


@register.simple_tag()
def change_country_name_to_include_the(country_name):
    countries_starting_with_the = [
        'bahamas',
        'cayman islands',
        'central african republic',
        'channel islands',
        'comoros',
        'czech republic',
        'dominican republic',
        'falkland islands',
        'faroe islands',
        'gambia',
        'isle of man',
        'ivory coast',
        'leeward islands',
        'maldives',
        'marshall islands',
        'netherlands',
        'netherlands antilles',
        'philippines',
        'solomon islands',
        'turks and caicos islands',
        'united arab emirates',
        'united kingdom',
        'united states',
        'virgin islands',
    ]

    if country_name.lower() in countries_starting_with_the:
        return f'the {country_name.lower().title().replace(" Of ", " of ").replace(" And ", " and ")}'
    return country_name.lower().title()


@register.filter
def guided_journey_mode(page_url):
    res = page_url.split('?')

    if len(res) == 2:
        return '?' + res[1]

    return ''


@register.filter
def get_sector_market_meta_label(selected_value):
    for val, label in META_LABELS:
        if selected_value == val:
            return label

    return ''


@register.filter
def get_exopps_country_slug(country):
    country_mappings = [('United States', 'the-usa')]

    for country_name, slug in country_mappings:
        if country == country_name:
            return slug

    return slugify(country.lower())


@register.filter
def get_visa_and_travel_country_slug(country):
    country_mappings = [
        ('Congo (Democratic Republic)', 'democratic-republic-of-the-congo'),
        ('Czechia', 'czech-republic'),
        ('East Timor', 'timor-leste'),
        ('Ivory Coast', 'cote-d-ivoire'),
        ('Myanmar (Burma)', 'myanmar'),
        ('St Vincent', 'st-vincent-and-the-grenadines'),
        ('The Bahamas', 'bahamas'),
        ('United States', 'usa'),
        ('Vatican City', 'italy'),
    ]

    for country_name, slug in country_mappings:
        if country == country_name:
            return slug

    return slugify(country.lower())


@register.filter
def get_visa_and_travel_url_for_eu_countries(country):
    for country_name, url in EU_TRAVEL_ADVICE_URLS:
        if country == country_name:
            return url

    return None


@register.filter
def split_title(title):
    title_parts = title.split('  ')

    return title_parts


@register.filter
def is_cheg_excluded_country(country_code):
    if country_code in CHEG_EXCLUDED_COUNTRY_CODES:
        return True

    return False


@register.filter
def convert_anchor_identifier_a_to_span(input_html):
    # find all <a> tags used as anchor identifiers, and replace with spans of same id
    soup = BeautifulSoup(input_html, 'html.parser')
    for anchor in soup.find_all('a', attrs={'linktype': 'anchor-target'}):
        new_tag = soup.new_tag('span')
        # Replicate <a> attributes on span and replace
        new_tag.string = anchor.string
        new_tag.attrs['data-id'] = anchor.attrs['data-id']
        new_tag.attrs['id'] = anchor.attrs['id']
        anchor.replace_with(new_tag)
    return mark_safe(str(soup))


@register.filter
def convert_anchor_identifiers_to_span(value):
    # Issue only occurs in content_modules where render_a method in core/rich_text.py does not fire, so return as-is
    if value.block_type != 'content_module':
        return value
    rich_text_html = value.value.content
    return convert_anchor_identifier_a_to_span(rich_text_html)


@register.inclusion_tag('_cta-banner.html')
def render_signup_cta(background=None, link=None):
    background_class = 'great-ds-cta-banner--bg-white'
    if background:
        background_class = f'great-ds-cta-banner--bg-{background}'

    link_color = ''
    if link:
        link_color = f'great-ds-action-link--{link}'

    return {
        'headingText': 'Accelerate your learning',
        'leadingText': "Sign up to Great.gov.uk and you'll be able to:",
        'listItems': [
            'Track your learning progress and read case studies',
            'Join live events from the UK Export Academy',
            'Compare markets using live export data',
        ],
        'backgroundClass': background_class,
        'actionLinkClass': link_color,
        'signInLink': {'href': '/login', 'preLinkText': 'Already signed up?', 'linkText': 'Sign in'},
        'signUpLink': {'href': '/signup', 'linkText': 'Sign up to get started'},
        'landscapeImagePath': '/static/images/lte-signup-promo-landscape.png',
        'portraitImagePath': '/static/images/lte-signup-promo-portrait.png',
    }


@register.filter
def sector_based_image(sector):
    res = None

    mapping = (
        ('Advanced manufacturing', 'industry'),
        ('Aerospace', 'plane'),
        ('Food and drink', 'carrot'),
    )

    for sector_name, icon_name in mapping:
        if sector == sector_name:
            res = icon_name

    return res


@register.filter
def is_a_dynamic_snippet(snippet_id):
    for snippet in DYNAMIC_SNIPPET_NAMES:
        if snippet[0] == snippet_id:
            return True

    return False


@register.filter
def get_card_meta_data_by_url(url):
    for url_match, text, icon_name in CARD_META_DATA:
        if url_match in url:
            return {
                'text': text,
                'icon_name': icon_name,
            }

    return {
        'text': False,
        'icon_name': False,
    }


@register.filter
def get_region_bg_class(postcode_data):
    region = postcode_data.get('region') if postcode_data.get('region') else postcode_data.get('country')

    for region_name, bg_class_name in REGION_IMAGES:
        if region == region_name:
            return bg_class_name

    return None


@register.filter
def get_url_favicon_and_domain(url):
    domain = urlsplit(url).netloc.replace('www.', '')

    domain_parts = domain.split('.')

    return {'filename': domain_parts[0], 'domain': domain}


@register.filter
def get_region_for_finance_and_support_snippet(postcode_data):
    region = postcode_data.get('region') if postcode_data.get('region') else postcode_data.get('country')

    for region_name, mapped_region_name in FINANCE_AND_SUPPORT_REGION_MAPPINGS:
        if region == region_name:
            return mapped_region_name

    return None


@register.filter
def get_region_name(postcode_data):
    region = postcode_data.get('region') if postcode_data.get('region') else postcode_data.get('country')

    return region


@register.filter
def get_region_for_find_a_grant_snippet(region):
    for region_name, mapped_region_name in FIND_A_GRANT_MAPPINGS:
        if region == region_name:
            return mapped_region_name

    return None


@register.filter
def get_is_internal_url(url):
    if INTERNAL_GREAT_DOMAIN in url or INTERNAL_BUSINESS_DOMAIN in url:
        return True
    return False
