from collections import Counter
from difflib import SequenceMatcher
from logging import getLogger
import csv
import functools

from directory_api_client import api_client
import great_components.helpers
from directory_constants import choices
from directory_sso_api_client import sso_api_client
from ipware import get_client_ip

from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.conf import settings

from .serializers import parse_opportunities, parse_events

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


def get_dashboard_events(sso_session_id):
    results = api_client.personalisation.events_by_location_list(sso_session_id)
    if (results.status_code == 200):
        return parse_events(results.json()['results'])
    else:
        return []


def get_dashboard_export_opportunities(company, sso_session_id):
    sectors = (company and company.expertise_industries_labels) or list(CompanyParser.SECTORS.values())
    search_term = ' '.join(sectors)
    results = api_client.personalisation.export_opportunities_by_relevance_list(sso_session_id, search_term)
    if (results.status_code == 200):
        return parse_opportunities(results.json()['results'])
    else:
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
