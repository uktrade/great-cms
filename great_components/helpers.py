from datetime import datetime
import urllib.parse

from django.utils.encoding import iri_to_uri
from django.utils import translation

from great_components import constants

from directory_constants import choices


COUNTRY_CODES = [code for code, _ in choices.COUNTRY_CHOICES]


def get_user(request):
    # backwards compatibility with new and old style of user auth
    for attribute in ['user', 'sso_user']:
        if hasattr(request, attribute):
            return getattr(request, attribute)


def get_is_authenticated(request):
    # backwards compatibility with new and old style of user auth
    user = get_user(request)
    if hasattr(user, 'is_authenticated'):
        return bool(user.is_authenticated)
    return user is not None


def add_next(destination_url, current_url):
    if 'next=' in destination_url:
        return destination_url
    concatenation_character = '&' if '?' in destination_url else '?'
    return '{url}{concatenation_character}next={next}'.format(
        url=destination_url,
        concatenation_character=concatenation_character,
        next=current_url,
    )


class SocialLinkBuilder:
    templates = (
        ('email', 'mailto:?body={url}&subject={body}'),
        ('twitter', 'https://twitter.com/intent/tweet?text={body}{url}'),
        ('facebook', 'https://www.facebook.com/share.php?u={url}'),
        (
            'linkedin',
            (
                'https://www.linkedin.com/shareArticle'
                '?mini=true&url={url}&title={body}&source=LinkedIn'
            )
        )
    )

    def __init__(self, url, page_title, app_title):
        self.url = url
        self.page_title = page_title
        self.app_title = app_title

    @property
    def body(self):
        body = '{app_title} - {page_title} '.format(
            app_title=self.app_title, page_title=self.page_title
        )
        return urllib.parse.quote(body)

    @property
    def links(self):
        return {
            name: template.format(url=self.url, body=self.body)
            for name, template in self.templates
        }


class UrlPrefixer:

    def __init__(self, request, prefix):
        self.prefix = prefix
        self.request = request

    @property
    def is_path_prefixed(self):
        return self.request.path.startswith(self.prefix)

    @property
    def path(self):
        return urllib.parse.urljoin(
            self.prefix, self.request.path.lstrip('/')
        )

    @property
    def full_path(self):
        path = self.path
        if not path.endswith('/'):
            path += '/'
        querystring = self.request.META.get('QUERY_STRING', '')
        if querystring:
            path += ('?' + iri_to_uri(querystring))
        return path


def get_country_from_querystring(request):
    country_code = request.GET.get('country')
    if country_code in COUNTRY_CODES:
        return country_code


def get_user_country(request):
    return get_country_from_querystring(request) or \
        request.COOKIES.get(constants.COUNTRY_COOKIE_NAME, '')


def get_language_from_querystring(request):
    language_code = request.GET.get('lang')
    language_codes = translation.trans_real.get_languages()
    if language_code and language_code in language_codes:
        return language_code


class CompanyParser:
    """
    Parse the company details provided by directory-api's company
    serializer

    """

    SECTORS = dict(choices.INDUSTRIES)
    EMPLOYEES = dict(choices.EMPLOYEES)
    INDUSTRIES = dict(choices.INDUSTRIES)
    COUNTRIES = dict(choices.COUNTRY_CHOICES)
    REGIONS = dict(choices.EXPERTISE_REGION_CHOICES)
    LANGUAGES = dict(choices.EXPERTISE_LANGUAGES)

    def __init__(self, data):
        self.data = data

    def __bool__(self):
        return bool(self.data)

    @property
    def is_publishable(self):
        return self.data['is_publishable']

    @property
    def date_of_creation(self):
        if self.data.get('date_of_creation'):
            date = datetime.strptime(self.data['date_of_creation'], '%Y-%m-%d')
            return date.strftime('%d %B %Y')

    @property
    def address(self):
        address = []
        fields = [
            'address_line_1', 'address_line_2', 'locality', 'postal_code'
        ]
        for field in fields:
            value = self.data.get(field)
            if value:
                address.append(value)
        return ', '.join(address)

    @property
    def keywords(self):
        if self.data.get('keywords'):
            return ', '.join(tokenize_keywords(self.data['keywords']))
        return ''

    @property
    def sectors_label(self):
        return values_to_labels(
            values=self.data.get('sectors') or [],
            choices=self.SECTORS
        )

    @property
    def employees_label(self):
        if self.data.get('employees'):
            return self.EMPLOYEES.get(self.data['employees'])

    @property
    def expertise_industries_label(self):
        return values_to_labels(
            values=self.data.get('expertise_industries') or [],
            choices=self.INDUSTRIES
        )

    @property
    def expertise_regions_label(self):
        return values_to_labels(
            values=self.data.get('expertise_regions') or [],
            choices=self.REGIONS
        )

    @property
    def expertise_countries_label(self):
        return values_to_labels(
            values=self.data.get('expertise_countries') or [],
            choices=self.COUNTRIES
        )

    @property
    def expertise_languages_label(self):
        return values_to_labels(
            values=self.data.get('expertise_languages') or [],
            choices=self.LANGUAGES
        )

    @property
    def is_in_companies_house(self):
        return self.data['company_type'] == 'COMPANIES_HOUSE'

    @property
    def has_expertise(self):
        fields = [
            'expertise_industries',
            'expertise_regions',
            'expertise_countries',
            'expertise_languages',
        ]
        return any(self.data.get(field) for field in fields)

    @property
    def expertise_products_services_label(self):
        value = self.data.get('expertise_products_services')
        if not value:
            return {}
        return {
            key.replace('-', ' ').capitalize(): ', '.join(value)
            for key, value in value.items()
        }


def values_to_labels(values, choices):
    return ', '.join([choices.get(item) for item in values if item in choices])


def tokenize_keywords(keywords):
    sanitized = keywords.replace(', ', ',').replace(' ,', ',').strip(' ,')
    return sanitized.split(',')


def get_pagination_url(request, page_param_name):
    """Remove pagination param from request url"""
    url = request.path
    params = request.GET.copy()
    params.pop(page_param_name, None)
    if params:
        return f'{url}?{params.urlencode()}&'
    return f'{url}?'
