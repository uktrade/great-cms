from collections import Counter
from difflib import SequenceMatcher
from logging import getLogger
import csv
from io import StringIO
import functools
from urllib.parse import urljoin

from directory_api_client import api_client
import great_components.helpers
from directory_constants import choices
from directory_sso_api_client import sso_api_client
from ipware import get_client_ip
import requests

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.conf import settings

from core.serializers import parse_opportunities, parse_events


USER_LOCATION_CREATE_ERROR = 'Unable to save user location'
USER_LOCATION_DETERMINE_ERROR = 'Unanble to determine user location'
COMMODITY_SEARCH_URL = urljoin(settings.DIT_HELPDESK_URL, '/search/api/commodity-term/')
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
        if self.data['expertise_countries']:
            return values_to_labels(values=self.data['expertise_countries'], choices=self.COUNTRIES)
        return []

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

    @property
    def expertise_products_value_label_pairs(self):
        return [{'value': item, 'label': item} for item in self.expertise_products_services]


def values_to_labels(values, choices):
    return [choices.get(item) for item in values if item in choices]


def values_to_value_label_pairs(values, choices):
    return [{'value': item, 'label': choices.get(item)} for item in values if item in choices]


def search_commodity_by_term(term, page=1):
    response = requests.get(COMMODITY_SEARCH_URL, {'q': term, 'page': page})
    response.raise_for_status()
    parsed = response.json()
    return [
        {'value': item['commodity_code'], 'label': item['description']}
        for item in parsed['results']
    ]


@functools.lru_cache(maxsize=None)
def get_popular_export_destinations(sector_label):
    export_destinations = Counter()
    for row in csv.DictReader(StringIO(countries_sectors), delimiter=','):
        row_sector_label = row['sector'].split(' :')[0]  # row has multi level delimited by ' :'. Get top level.
        if is_fuzzy_match(label_a=row_sector_label, label_b=sector_label):
            export_destinations.update([row['country']])
    return export_destinations.most_common(5)


@functools.lru_cache(maxsize=None)
def get_country_population(name, year):
    # returns thousands
    for row in csv.reader(StringIO(country_population_data), delimiter=','):
        if is_fuzzy_match(label_a=name, label_b=row[2]) and row[7] == str(year):
            return int(float(row[29].replace(',', '')))


@functools.lru_cache(maxsize=None)
def get_country_population_by_age_range(name, year, age_range, sex_filter=None):
    # returns thousands
    assert age_range in population_age_range_choices

    dataset = {
        MALE: country_population_data_male,
        FEMALE: country_population_data_female,
        None: country_population_data,
    }[sex_filter]

    for row in csv.reader(StringIO(dataset), delimiter=','):
        if is_fuzzy_match(label_a=name, label_b=row[2]) and row[7] == str(year):
            # age range column starts at index 8
            index = population_age_range_choices.index(age_range) + 8
            return int(float(row[index].replace(' ', '')))


@functools.lru_cache(maxsize=None)
def get_country_average_income(name, year):
    # in USD
    for row in csv.reader(StringIO(country_average_income_data), delimiter=','):
        if is_fuzzy_match(label_a=name, label_b=row[0]):
            return int(float(row[-1]))


@functools.lru_cache(maxsize=None)
def get_country_urban_percentage(name, year):
    for row in csv.reader(StringIO(country_urban_rural_data), delimiter=','):
        if is_fuzzy_match(label_a=name, label_b=row[1]):
            return float(row[7])


@functools.lru_cache(maxsize=None)
def get_country_consumer_price_index(name, year):
    for row in csv.reader(StringIO(country_consumer_price_index_data), delimiter=','):
        if is_fuzzy_match(label_a=name, label_b=row[0]):
            index = 4 + year - 1960  # year columns start at column 4, it's year 1960
            return round(float(row[index]), 2)
