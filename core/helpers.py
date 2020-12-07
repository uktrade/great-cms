from collections import Counter
from difflib import SequenceMatcher
from logging import getLogger
from io import StringIO
from ipware import get_client_ip

import csv
import functools
import requests

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.conf import settings

import great_components.helpers
from directory_api_client import api_client
from directory_constants import choices
from directory_sso_api_client import sso_api_client

from core.serializers import parse_opportunities, parse_events
from core.models import CuratedListPage


USER_LOCATION_CREATE_ERROR = 'Unable to save user location'
USER_LOCATION_DETERMINE_ERROR = 'Unable to determine user location'
MALE = 'xy'
FEMALE = 'xx'


logger = getLogger(__name__)


with open(settings.ROOT_DIR + 'core/fixtures/countries-populations.csv', 'r') as f:
    country_population_data = f.read()


with open(settings.ROOT_DIR + 'core/fixtures/countries-populations-male.csv', 'r') as f:
    country_population_data_male = f.read()


with open(settings.ROOT_DIR + 'core/fixtures/countries-populations-female.csv', 'r') as f:
    country_population_data_female = f.read()


with open(settings.ROOT_DIR + 'core/fixtures/countries-sectors-export.csv', 'r') as f:
    countries_sectors = f.read()


with open(settings.ROOT_DIR + 'core/fixtures/countries-average-income.csv', 'r') as f:
    country_average_income_data = f.read()


with open(settings.ROOT_DIR + 'core/fixtures/countries-urban-rural.csv', 'r') as f:
    country_urban_rural_data = f.read()


with open(settings.ROOT_DIR + 'core/fixtures/countries-consumer-price-index.csv', 'r') as f:
    country_consumer_price_index_data = f.read()


population_age_range_choices = [
    '0-8',
    '5-9',
    '10-14',
    '15-19',
    '20-24',
    '25-29',
    '30-34',
    '35-39',
    '40-44',
    '45-49',
    '50-54',
    '55-59',
    '60-64',
    '65-69',
    '70-74',
    '75-79',
    '80-84',
    '85-89',
    '90-94',
    '95-99',
    '100+',
]


def get_location(request):
    client_ip, is_routable = get_client_ip(request)
    if client_ip and is_routable:
        try:
            city = GeoIP2().city(client_ip)
        except GeoIP2Exception:
            logger.error(USER_LOCATION_DETERMINE_ERROR)
        else:
            return {
                'country': city['country_code'],
                'region': city['region'],
                'latitude': city['latitude'],
                'longitude': city['longitude'],
                'city': city['city'],
            }


def store_user_location(request):
    location = get_location(request)
    if location:
        response = api_client.personalisation.user_location_create(
            sso_session_id=request.user.session_id,
            data=location
        )
        if not response.ok:
            logger.error(USER_LOCATION_CREATE_ERROR)


def update_company_profile(data, sso_session_id):
    response = api_client.company.profile_update(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response


def create_user_profile(data, sso_session_id):
    response = sso_api_client.user.create_user_profile(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response


def get_dashboard_events(sso_session_id):
    results = api_client.personalisation.events_by_location_list(sso_session_id)
    if (results.status_code == 200):
        return parse_events(results.json()['results'])
    return []


def get_dashboard_export_opportunities(sso_session_id, company):
    sectors = company.expertise_industries_labels if company else []
    search_term = ' '.join(sectors)
    results = api_client.personalisation.export_opportunities_by_relevance_list(sso_session_id, search_term)
    if (results.status_code == 200):
        return parse_opportunities(results.json()['results'])
    return []


def get_custom_duties_url(product_code, country):
    return f'{settings.MADB_URL}/summary?d={country}&pc={product_code}'


def get_markets_page_title(company):
    industries, countries = company.data['expertise_industries'], company.data['expertise_countries']
    if industries and countries:
        return f'The {company.expertise_industries_labels[0]} market in {company.expertise_countries_label}'
    elif industries:
        return f'The {company.expertise_industries_labels[0]} market'
    elif countries:
        return f'The market in {company.expertise_countries_label}'


def get_canonical_sector_label(label):
    return label.lower().replace(' & ', ' and ')


@functools.lru_cache(maxsize=None)
def is_fuzzy_match(label_a, label_b):
    match = SequenceMatcher(None, get_canonical_sector_label(label_a), get_canonical_sector_label(label_b))
    return match.ratio() > 0.9


class CompanyParser(great_components.helpers.CompanyParser):

    INDUSTRIES = dict(choices.SECTORS)  # defaults to choices.INDUSTRIES

    def __init__(self, data):
        data = {**data}
        data.setdefault('expertise_products_services', {})
        data.setdefault('expertise_countries', [])
        data.setdefault('expertise_industries', [])
        if settings.FEATURE_FLAG_HARD_CODE_USER_INDUSTRIES_EXPERTISE:
            data['expertise_industries'] = ['SL10017']  # food and drink
        super().__init__(data=data)

    def __getattr__(self, name):
        return self.data.get(name)

    @property
    def expertise_industries_labels(self):
        if self.data['expertise_industries']:
            return values_to_labels(values=self.data['expertise_industries'], choices=self.INDUSTRIES)
        return []

    @property
    def expertise_countries_labels(self):
        return values_to_labels(
            values=self.data['expertise_countries'], choices=self.COUNTRIES
        ) if self.data.get('expertise_countries') else []

    @property
    def expertise_countries_value_label_pairs(self):
        if self.data['expertise_countries']:
            return values_to_value_label_pairs(values=self.data['expertise_countries'], choices=self.COUNTRIES)
        return []

    @property
    def expertise_industries_value_label_pairs(self):
        if self.data['expertise_industries']:
            return values_to_value_label_pairs(values=self.data['expertise_industries'], choices=self.INDUSTRIES)
        return []

    @property
    def expertise_products_services(self):
        return self.data['expertise_products_services'].get('other', [])


def values_to_labels(values, choices):
    return [choices.get(item) for item in values if item in choices]


def values_to_value_label_pairs(values, choices):
    return [{'value': item, 'label': choices.get(item)} for item in values if item in choices]


def search_commodity_by_term(term, json=True):
    response = requests.post(
        url=settings.COMMODITY_SEARCH_URL,
        json={
            'origin': 'GB',
            'proddesc': term,
            'state': 'start',
            'stopAtHS6': 'Y',
            'schedule': 'import/export',
        },
        headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'Authorization': settings.COMMODITY_SEARCH_TOKEN,
        }
    )

    response.raise_for_status()
    return response.json() if json else response


def search_commodity_refine(interaction_id, tx_id, values):
    response = requests.post(
        url=settings.COMMODITY_SEARCH_REFINE_URL,
        json={
            'origin': 'GB',
            'state': 'continue',
            'stopAtHS6': 'Y',
            'txid': tx_id,
            'interactionid': interaction_id,
            'values': values,
        },
        headers={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
            'Authorization': settings.COMMODITY_SEARCH_TOKEN,
        }
    )
    response.raise_for_status()
    return response.json()


@functools.lru_cache(maxsize=None)
def get_popular_export_destinations(sector_label):
    export_destinations = Counter()
    for row in csv.DictReader(StringIO(countries_sectors), delimiter=','):
        row_sector_label = row['sector'].split(' :')[0]  # row has multi level delimited by ' :'. Get top level.
        if is_fuzzy_match(label_a=row_sector_label, label_b=sector_label):
            export_destinations.update([row['country']])
    return export_destinations.most_common(5)


def get_module_completion_progress(completion_status, module_page: CuratedListPage):
    """Returns per-module completion data, with lesson-level detail. Completed
    lessons are grouped by the topic they belong to.

    `completion_status` is the output of from domestic.helpers.get_lesson_completion_status

    """

    for module_data in completion_status.get('module_pages', []):
        if module_data['page'].id == module_page.id:
            return module_data

    return {}


def _percent_completion_for_module(module_data: dict) -> int:
    """Produce a rough, integer-rounded completion percentage for the
    given module."""

    try:
        pc = module_data['completion_count'] / module_data['total_pages'] * 100
        return round(pc)
    except (KeyError, ZeroDivisionError):
        pass

    return 0  # Fallback: nothing can be completed if the above data isn't valid


def get_high_level_completion_progress(completion_status):
    """Return a dictionary of overall completion data for each
    module/CuratedListPage, with module-level stats, but no details
    on specific lessons.

    `completion_status` is the output of from domestic.helpers.get_lesson_completion_status
    """

    # Transform list of modules from a list into a dict so we can get them
    # more easily, plus add in a completion percentage
    repackaged_output = {}
    for module_data in completion_status.get('module_pages', []):
        repackaged_output[module_data['page'].id] = {
            'total_pages': module_data.get('total_pages', 0),
            'completion_count': module_data.get('completion_count', 0),
            'completion_percentage': _percent_completion_for_module(module_data),
        }

    return repackaged_output


def get_suggested_countries_by_hs_code(sso_session_id, hs_code):
    response = api_client.dataservices.suggested_countries_by_hs_code(hs_code=hs_code)
    response.raise_for_status()
    return response.json()


def get_sender_ip_address(request):
    ip, is_routable = get_client_ip(request)
    return ip or None
