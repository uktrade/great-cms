from collections import Counter
from difflib import SequenceMatcher
from logging import getLogger
import csv
import functools
from random import choice

from directory_api_client import api_client
import great_components.helpers
from directory_constants import choices
from directory_sso_api_client import sso_api_client
from ipware import get_client_ip

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.conf import settings

USER_LOCATION_CREATE_ERROR = 'Unable to save user location'
USER_LOCATION_DETERMINE_ERROR = 'Unanble to determine user location'

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


def create_company_profile(data):
    response = api_client.enrolment.send_form(data)
    response.raise_for_status()
    return response


def update_company_profile(data, sso_session_id):
    response = api_client.company.profile_update(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response


def create_user_profile(data, sso_session_id):
    response = sso_api_client.user.create_user_profile(sso_session_id=sso_session_id, data=data)
    response.raise_for_status()
    return response


def get_dashboard_events(company):
    sectors = (company and company.expertise_industries_labels) or list(CompanyParser.SECTORS.values())
    return [
        {
            'title': f'{choice(sectors)} taster visit to Bruges',
            'description': 'Join the Department for international Trade (DIT) and Northern...',
            'url': '#',
            'location': 'London',
            'date': '11 Feb 2020',
        },
        {
            'title': f'{choice(sectors)} visit to London',
            'description': (
                'Join the Department for international Trade (DIT) and Northern England with the great real...'
            ),
            'url': '#',
            'location': 'London',
            'date': '11 Feb 2020',
        },
        {
            'title': f'{choice(sectors)} event in Paris',
            'description': (
                'Join the Department for international Trade (DIT) and Northern England with the great real...'
            ),
            'url': '#',
            'location': 'London',
            'date': '11 Feb 2020',
        }
    ]


def get_dashboard_export_opportunities(company):
    countries = (company and company.expertise_countries_labels) or list(CompanyParser.COUNTRIES.values())
    sectors = (company and company.expertise_industries_labels) or list(CompanyParser.SECTORS.values())
    return [
        {
            'title': f'{choice(sectors)} needed in {choice(countries)}',
            'description': '',
            'provider': 'OpenOpps',
            'provider_image': '/path/to/shamrock',
            'url': '#',
            'published_data': '11 Feb 2020',
            'closing_data': '11 March 2020',
        },
        {
            'title': f'{choice(countries)} - {choice(sectors)} required',
            'description': "A company is looking products to sell in it's branches",
            'provider': '',
            'provider_image': '',
            'url': '#',
            'published_data': '10 March 2020',
            'closing_data': '15 December 2020',
        },
        {
            'title': f'{choice(countries)} - {choice(sectors)} products',
            'description': "A company is looking for products to sell in it's branches",
            'provider': '',
            'provider_image': '',
            'url': '#',
            'published_data': '03 January 2020',
            'closing_data': '05 June 2020',
        }
    ]


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
            row_sectors = row['sector'].split(' :')[0]  # row has multi level delimited by ' :'. Get top level.
            if is_fuzzy_match(label_a=row_sectors, label_b=sector_label):
                export_destinations.update([row['country']])
    return export_destinations.most_common(5)


class CompanyParser(great_components.helpers.CompanyParser):

    INDUSTRIES = dict(choices.SECTORS)  # defaults to choices.INDUSTRIES

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


def values_to_labels(values, choices):
    return [choices.get(item) for item in values if item in choices]
