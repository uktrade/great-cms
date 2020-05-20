from collections import Counter
from difflib import SequenceMatcher
from logging import getLogger
import csv
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


logger = getLogger(__name__)


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


def get_popular_export_destinations(sector_label):
    export_destinations = Counter()

    with open(settings.ROOT_DIR + 'core/fixtures/countries-sectors-export.csv', 'r') as f:
        for row in csv.DictReader(f, delimiter=','):
            row_sector_label = row['sector'].split(' :')[0]  # row has multi level delimited by ' :'. Get top level.
            if is_fuzzy_match(label_a=row_sector_label, label_b=sector_label):
                export_destinations.update([row['country']])
    return export_destinations.most_common(5)


class CompanyParser(great_components.helpers.CompanyParser):

    INDUSTRIES = dict(choices.SECTORS)  # defaults to choices.INDUSTRIES

    def __init__(self, data):
        data = {**data}
        data.setdefault('expertise_products_services', {})
        if settings.FEATURE_FLAG_HARD_CODE_USER_INDUSTRIES_EXPERTISE:
            data['expertise_industries'] = ['SL10017']  # food and drink
        super().__init__(data=data)

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

    @property
    def logo(self):
        return self.data.get('logo')


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


def country_by_iso_code(term):
    country_data = all_country_data()[term]

    wb_request = requests.get(
        'http://api.worldbank.org/v2/country/' + term + '?format=json'
    )
    wb_request.raise_for_status()
    wb_data = wb_request.json()

    if wb_request.status_code == 200 and 'total' in wb_data[0]:
        country_data['name'] = wb_data[1][0]['name']
        country_data['region'] = wb_data[1][0]['region']['value']
        country_data['development_level'] = wb_data[1][0]['incomeLevel']['value']
        country_data['capital'] = wb_data[1][0]['capitalCity']

    return country_data


def countries_by_iso_code():
    return all_country_data()


def all_country_data():
    return {
        'AUS': {
            'currency_name': 'the Australian Dollar',
            'purchasing_power_parity': '1.43',
            'imports': {
                'year_of_latest_data': '2019',
                'cost_to_import': 'USD $639',
                'lead_time_to_import': '5 days',
            }
        },
        'BR': {
            'currency_name': 'the Real',
            'purchasing_power_parity': '2.03',
            'imports': {
                'year_of_latest_data': '2019',
                'cost_to_import': 'USD $481',
                'lead_time_to_import': '8 days',
            }
        },
        'CN': {
            'currency_name': 'the Yuan',
            'purchasing_power_parity': '3.56',
            'imports': {
                'year_of_latest_data': '2019',
                'cost_to_import': 'USD $318',
                'lead_time_to_import': '6 days',
            }
        },
        'FR': {
            'currency_name': 'the Euro',
            'purchasing_power_parity': '0.77',
            'imports': {
                'year_of_latest_data': '2019',
                'cost_to_import': 'USD $0',
                'lead_time_to_import': '2 days',
            }
        },
        'DE': {
            'currency_name': 'the Euro',
            'purchasing_power_parity': '0.76',
            'imports': {
                'year_of_latest_data': '2019',
                'cost_to_import': 'USD $0',
                'lead_time_to_import': '2 days',
            }
        },
        'IND': {
            'currency_name': 'the Indian Rupee',
            'purchasing_power_parity': '18.13',
            'imports': {
                'year_of_latest_data': '2019',
                'cost_to_import': 'USD $366',
                'lead_time_to_import': '4 days',
            }
        },
        'US': {
            'currency_name': 'the Dollar',
            'purchasing_power_parity': '1',
            'imports': {
                'year_of_latest_data': '2019',
                'cost_to_import': 'USD $275',
                'lead_time_to_import': '5 days',
            }
        }
    }
