# Refactored/amended versions of templatetags formerly in directory_componennts
from bs4 import BeautifulSoup
from django import template
from django.templatetags import static
from django.urls import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe

from core.helpers import get_markets_list
from domestic.helpers import (
    get_market_widget_data_helper,
    get_sector_and_market_promo_data_helper,
    get_sector_widget_data_helper,
)
from domestic_growth.models import DomesticGrowthContent

register = template.Library()

META_DESCRIPTION_TEXT_LENGTH = 150


@register.tag
def breadcrumbs(parser, token):
    nodelist = parser.parse(('endbreadcrumbs',))
    parser.delete_first_token()
    return Breadcrumbs(nodelist)


class Breadcrumbs(template.Node):
    template = """
        <nav aria-label="Breadcrumb" class="{class_style}">
          <ol>
          </ol>
        </nav>
    """

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        try:
            class_style = self.token.split_contents()[1]
        except IndexError:
            class_style = 'breadcrumbs'
        html = self.nodelist.render(context)
        input_soup = BeautifulSoup(html, 'html.parser')
        output_soup = BeautifulSoup(self.template.format(class_style=class_style), 'html.parser')
        links = input_soup.findAll('a')
        if not links:
            raise ValueError('Please specify some links')
        # adding level 1...n
        for link in links:
            if not link.get('href'):
                raise ValueError('Missing href in breadcrumb')
            element = output_soup.new_tag('li')
            element.append(link)
            output_soup.find('ol').append(element)

        # remove tabbing through breadcrumbs
        output = output_soup.findAll('a')
        for anchor in output:
            anchor['tabindex'] = '-1'

        return output_soup.decode(formatter=None)


@register.tag
def ga360_data(parser, token):
    nodelist = parser.parse(('end_ga360_data',))
    parser.delete_first_token()

    # the ga360_data tag expects arguments in the following format
    # <target> action=<action> type=<type> element=<element> value=<value>
    parameters = token.split_contents()

    target = parameters[1]
    action = None
    ga_type = None
    element = None
    value = None
    include_form_data = None

    for parameter in parameters[2:]:
        action_param_name = 'action='
        type_param_name = 'type='
        element_param_name = 'element='
        value_param_name = 'value='
        include_form_data_param_name = 'include_form_data='

        if parameter.startswith(action_param_name):
            action = parameter[len(action_param_name) :]  # noqa: E203

        elif parameter.startswith(type_param_name):
            ga_type = parameter[len(type_param_name) :]  # noqa: E203

        elif parameter.startswith(element_param_name):
            element = parameter[len(element_param_name) :]  # noqa: E203

        elif parameter.startswith(value_param_name):
            value = parameter[len(value_param_name) :]  # noqa: E203

        elif parameter.startswith(include_form_data_param_name):
            include_form_data = parameter[len(include_form_data_param_name) :]  # noqa: E203

    return GA360Data(nodelist, target, action, ga_type, element, value, include_form_data)  # /PS-IGNORE


class GA360Data(template.Node):  # /PS-IGNORE
    def __init__(self, nodelist, target, action=None, ga_type=None, element=None, value=None, include_form_data=None):
        self.nodelist = nodelist
        self.target = template.Variable(target)
        self.action = template.Variable(action) if action is not None else None
        self.ga_type = template.Variable(ga_type) if ga_type is not None else None
        self.element = template.Variable(element) if element is not None else None
        self.value = template.Variable(value) if value is not None else None
        self.include_form_data = template.Variable(include_form_data) if include_form_data is not None else None

    def render(self, context):
        html = self.nodelist.render(context)
        soup = BeautifulSoup(html, 'html.parser')

        selector = self.target.resolve(context)
        for element in soup.findAll(selector):
            if self.action is not None:
                element.attrs['data-ga-action'] = self.action.resolve(context)
            if self.ga_type is not None:
                element.attrs['data-ga-type'] = self.ga_type.resolve(context)
            if self.element is not None:
                element.attrs['data-ga-element'] = self.element.resolve(context)
            if self.value is not None:
                element.attrs['data-ga-value'] = self.value.resolve(context)
            if self.include_form_data is not None:
                element.attrs['data-ga-include-form-data'] = self.include_form_data.resolve(context)

        # Use formatter=None so that `&` is not converted to `&amp;`
        return soup.decode(formatter=None)


class FullStaticNode(static.StaticNode):
    def url(self, context):
        request = context['request']
        return request.build_absolute_uri(super().url(context))


@register.tag
def static_absolute(parser, token):
    return FullStaticNode.handle_token(parser, token)


@register.filter
def industry_accordion_is_viable(value):
    # Decides whether or not to show an industry accordion,
    # based on the value of a CountryGuideIndustryBlock
    if not value:
        return False

    return all([value.get('title'), value.get('teaser'), len(value.get('subsections')) > 1])


@register.filter
def industry_accordion_case_study_is_viable(value):
    # Decides whether or not to show an industry accordion,
    # based on the value of a CountryGuideCaseStudyBlock
    if not value:
        return False
    return all([value.get('title'), value.get('hero_image')])


@register.simple_tag
def get_meta_description(page):
    if not page:
        return ''

    description = page.article_teaser if page.article_teaser else page.search_description

    if not description and page.article_body:
        #  article_body is a streamfield with rich-text blocks in it

        html = BeautifulSoup(
            page.article_body.render_as_block(),
            'html.parser',
            # Note that this excludes pull quotes
        )
        body_text = html.findAll(text=True)
        description = ''.join(body_text)[:META_DESCRIPTION_TEXT_LENGTH]

    return description if description is not None else ''


def get_pagination_url(request, page_param_name):
    """Remove pagination param from request url"""
    url = request.path
    params = request.GET.copy()
    params.pop(page_param_name, None)
    if params:
        return f'{url}?{params.urlencode()}&'
    return f'{url}?'


@register.inclusion_tag('_numbered_pagination.html', takes_context=True)
def pagination(context, page_obj, page_param_name='page', elided_page_range=None, hover_classes=None):
    current_url = get_pagination_url(request=context['request'], page_param_name=page_param_name)

    context = {
        'currentPageURL': current_url,
        'elidedPageRange': elided_page_range,
        'elidedPageStr': '…',  # Copied from django pagination output
        'pageParamName': page_param_name,
        'hoverClasses': hover_classes,
    }

    context['previousPageNumber'] = page_obj.previous_page_number() if page_obj.has_previous() else None
    context['currentPageNumber'] = page_obj.number
    context['nextPageNumber'] = page_obj.next_page_number() if page_obj.has_next() else None
    context['lastPageNumber'] = page_obj.paginator.num_pages

    return context


@register.filter
def pagination_obj_range_lower_limit(page_obj):
    current_page_number = page_obj.number
    per_page = page_obj.paginator.per_page

    if current_page_number == 1:
        return 1

    lower_limit = (per_page * (current_page_number - 1)) + 1

    return lower_limit


@register.filter
def pagination_obj_range_upper_limit(page_obj):
    total_objects = page_obj.paginator.count
    current_page_number = page_obj.number
    per_page = page_obj.paginator.per_page

    upper_limit = per_page * current_page_number

    if upper_limit > total_objects:
        upper_limit = total_objects
    return upper_limit


@register.inclusion_tag('components/message_box.html')
def message_box(**kwargs):
    return kwargs


@register.inclusion_tag('components/message_box_with_icon.html')
def success_box(**kwargs):
    return {
        'icon': '✓',
        'heading_level': 'h3',
        **kwargs,
    }


@register.inclusion_tag('components/message_box_with_icon.html')
def error_box(**kwargs):
    return {
        'icon': '✕',
        'border_colour': 'flag-red',
        'heading_class': 'heading-xlarge flag-red-text',
        'box_class': 'width-full background-white flag-red-text',
        'heading': '.heading-large .flag-red-text',
        'description': '.width-two-thirds .background-white .flag-red-text',
        'heading_level': 'h3',
        **kwargs,
    }


@register.inclusion_tag('components/message_box_with_icon.html')
def message_box_with_icon(**kwargs):
    return kwargs


@register.simple_tag
def get_projected_or_actual(is_projected, capitalise=False):
    if is_projected:
        projected_or_actual = 'projected'
    else:
        projected_or_actual = 'actual'

    if capitalise:
        return projected_or_actual.title()
    else:
        return projected_or_actual


@register.filter
def append_past_year_seperator(events):
    years = set()
    for event in events:
        start_date = event.start_date
        year = start_date.strftime('%Y')
        if year not in years and start_date < timezone.now():
            event.past_year_seperator = year
            years.add(year)
        else:
            event.past_year_seperator = None

    return events


@register.filter
def persist_language(url, query_params=None):
    if query_params.get('lang'):
        return f"{url}?lang={query_params.get('lang')}"
    return url


@register.filter(name='replace_underscores')
def replace_underscores(value, replacement='-'):
    return value.replace('_', replacement)


@register.filter(name='replace_hyphens')
def replace_hyphens(value, replacement='_'):
    return value.replace('-', replacement)


@register.filter(name='remove_string')
def remove_string(value, replacement=''):
    return value.replace('.', replacement)


@register.filter
def get_market_widget_data(market):
    return get_market_widget_data_helper(market)


@register.filter
def get_sector_widget_data(sector):
    return get_sector_widget_data_helper(sector)


@register.filter
def get_sector_and_market_promo_data(session_data):
    sector = 'None'
    market = 'None'
    exporter_type = 'goods'

    if session_data.get('sector'):
        sector = session_data.get('sector')

    if session_data.get('market'):
        market = session_data.get('market')

    if session_data.get('exporter_type'):
        exporter_type = session_data.get('exporter_type')

    return get_sector_and_market_promo_data_helper(sector, market, exporter_type)


@register.filter
def get_market_code(market):
    country_code = ''
    countries = get_markets_list()

    for code, name in countries:
        if name == market:
            country_code = code

    return country_code.lower()


# Design system call to action banner componenents
@register.inclusion_tag('_cta-banner.html')
def render_markets_cta():
    return {
        'backgroundClass': 'great-ds-cta-banner--bg-green',
        'actionLinkClass': 'great-ds-action-link--black',
        'headingText': 'Kick start your exporting journey today',
        'leadingText': 'Learn how to export, find the right market and develop an export plan.',
        'signUpLink': {'href': '/dashboard', 'linkText': 'Get started'},
        'landscapeImagePath': '/static/images/markets-cta-image.png',
    }


@register.inclusion_tag('_cta-banner.html')
def render_finance_cta(page):
    return {
        'headingText': mark_safe(page.contact_proposition),
        'leadingText': '',
        'signUpLink': {
            'href': reverse('domestic:uk-export-finance-lead-generation-form', kwargs={'step': 'contact'}),
            'linkText': page.contact_button,
        },
    }


@register.inclusion_tag('_cta-banner.html')
def render_market_article_cta(page):
    return {
        'headingText': page.cta_title,
        'leadingText': page.cta_teaser,
        'signUpLink': {'href': page.cta_link, 'linkText': page.cta_link_label},
    }


# Design system hero componenents
@register.inclusion_tag('_hero.html')
def render_event_list_hero(image_url, hero_title, text, conditional_text):
    if text and conditional_text:
        description_html = text + '<br>' + conditional_text
    else:
        description_html = text
    return {
        'pngImagePath': image_url,
        'heading': hero_title,
        'aboveCtaHtml': description_html,
        'classes': 'great-ds-hero--bg-white great-ds-hero--box-shadow great-ds-hero--large-image-cropping',
    }


# UKEA and FAB share logged-in/logged-out hero cta patterns, so share this tag
@register.inclusion_tag('_hero.html')
def render_ukea_and_fab_homepage_heros(
    image_url,
    hero_title,
    above_cta_text,
    below_cta_text,
    action_link_label,
    action_link_internal,
    action_link_external,
):
    if not action_link_label and (action_link_internal or action_link_external):
        action_link_label = None
        action_link_url = None
    elif action_link_internal:
        action_link_url = action_link_internal
    else:
        action_link_url = action_link_external

    return {
        'pngImagePath': image_url,
        'heading': hero_title,
        'aboveCtaHtml': above_cta_text,
        'belowCtaHtml': below_cta_text,
        'classes': 'great-ds-hero--bg-white great-ds-hero--box-shadow great-ds-hero--large-image-cropping',
        'actionLinkUrl': action_link_url,
        'actionLinkText': action_link_label,
    }


@register.inclusion_tag('_hero.html')
def render_event_details_hero(
    image_url,
    event_type,
    event_name,
    event_dates,
):

    # Convert to local timezone to ensure correct time display
    local_event_date = timezone.localtime(event_dates)

    # Use %-I to get hour without leading zero in 12-hour format ('4:05pm' instead of '04:05pm')
    event_date_string = local_event_date.strftime('%A %d %B at %-I:%M%p')

    if event_type:
        caption = event_type.capitalize() + ' event'
    else:
        caption = 'Event'

    return {
        'pngImagePath': image_url,
        'caption': caption,
        'heading': event_name,
        'aboveCtaText': event_date_string,
        'classes': 'great-ds-hero--bg-white great-ds-hero--small-image',
        'aboveCtaClasses': 'great-text-grey',
    }


@register.inclusion_tag('_hero.html')
def render_ukea_course_hero(
    image_url,
    hero_title,
    hero_caption,
    above_cta_description_html,
    signed_in,
    course_slug,
):
    action_link_url = None
    action_link_label = None
    description_html = None
    if not signed_in:
        signup_url = reverse('export_academy:signup')
        signin_url = reverse('export_academy:signin')
        next_url = reverse('export_academy:course', args={course_slug})
        action_link_url = signup_url + '?next=' + next_url
        action_link_label = 'Sign up to get started'
        description_url = signin_url + '?next=' + next_url
        description_html = "<p> Already joined the UK Export Academy? <a href='" + description_url + "'>Sign in</a></p>"

    return {
        'pngImagePath': image_url,
        'heading': hero_title,
        'caption': hero_caption,
        'aboveCtaHtml': above_cta_description_html,
        'belowCtaHtml': description_html,
        'actionLinkUrl': action_link_url,
        'actionLinkText': action_link_label,
        'classes': 'great-ds-hero--bg-white great-ds-hero--large-image-cropping',
        'aboveCtaClasses': 'govuk-link--no-visited-state',
    }


@register.inclusion_tag('_hero.html')
def render_export_plan_hero(
    image_url,
    hero_title,
    above_cta_text,
    action_link_label,
    action_link_url_name,
):
    action_link_url = reverse(action_link_url_name)
    return {
        'pngImagePath': image_url,
        'heading': hero_title,
        'aboveCtaHtml': above_cta_text,
        'classes': 'great-ds-hero--bg-white great-ds-hero--large-image-cropping',
        'actionLinkUrl': action_link_url,
        'actionLinkText': action_link_label,
    }


@register.inclusion_tag('_hero.html')
def render_account_hero(image_url, hero_title, hero_text=None, email=None):
    if hero_text and email:
        hero_text = hero_text + email + '.'
    return {
        'pngImagePath': image_url,
        'heading': hero_title,
        'aboveCtaText': hero_text,
        'classes': 'great-ds-hero--bg-white great-ds-hero--box-shadow great-ds-hero--large-image-cropping',
    }


@register.filter
def get_lte_hero_image_path_from_class(title):
    get_started_header_img = '/static/images/learn-to-export-topic1-header.png'
    identify_opportunities_header_img = '/static/images/learn-to-export-topic2-header.png'
    prepare_to_sell_header_img = '/static/images/learn-to-export-topic3-header.png'
    regulations_licensing_header_img = '/static/images/learn-to-export-topic4-header.png'
    funding_financing_header_img = '/static/images/learn-to-export-topic5-header.png'

    title_to_image_path_map = {
        'get-started': get_started_header_img,
        'identify-opportunities-and-research-the-market': identify_opportunities_header_img,
        'prepare-to-sell-into-a-new-country': prepare_to_sell_header_img,
        'regulations-licensing-and-logistics': regulations_licensing_header_img,
        'funding-financing-and-getting-paid': funding_financing_header_img,
    }

    if title in title_to_image_path_map.keys():
        return str(title_to_image_path_map[title])
    else:
        return ''


@register.filter
def regional_snippet(snippet, region):
    content_snippets = DomesticGrowthContent.objects.all()

    filtered_snippets = list(
        content_snippets.filter(content_id__contains=str(snippet.content_id), region__contains=str(region))
    )

    if len(filtered_snippets) >= 1:
        return filtered_snippets[0]

    return None


@register.filter
def sector_snippet(snippet, sector):
    content_snippets = DomesticGrowthContent.objects.all()

    filtered_snippets = list(
        content_snippets.filter(content_id__contains=str(snippet.content_id), sector__contains=str(sector))
    )

    if len(filtered_snippets) >= 1:
        return filtered_snippets[0]

    return None
