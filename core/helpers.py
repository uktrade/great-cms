import csv
import functools
import math
import re
import time
import urllib
from collections import Counter
from difflib import SequenceMatcher
from io import StringIO
from logging import getLogger

import boto3
import great_components.helpers
import requests
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.shortcuts import redirect
from django.utils.functional import cached_property
from ipware import get_client_ip

from core.models import CuratedListPage
from core.serializers import parse_opportunities
from directory_api_client import api_client
from directory_constants import choices
from directory_sso_api_client import sso_api_client

USER_LOCATION_CREATE_ERROR = 'Unable to save user location'
USER_LOCATION_DETERMINE_ERROR = 'Unable to determine user location'
MALE = 'xy'
FEMALE = 'xx'


logger = getLogger(__name__)


def age_group_mapping(target_ages):
    # Rather than hardcode a mapping - this fn takes an array of input age ranges and outputs
    # mappings in 5 year sections up to 100 to match world-bank data
    # e.g. ('35-44','45-54') would map to ['35-39', '40-44', '45-49', '50-54']
    out = []
    for range_str in target_ages:
        range = re.split(r'[-+]', range_str)
        range[1] = range[1] or '101'
        start = int(range[0])
        while start < int(range[1]):
            if start >= 100:
                out.append('100+')
            else:
                out.append(f'{start}-{start+4}')
            start += 5
    return out


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
            sso_session_id=request.user.session_id, data=location
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


def get_dashboard_export_opportunities(sso_session_id, company):
    sectors = company.expertise_industries_labels if company else []
    search_term = ' '.join(sectors)
    results = api_client.personalisation.export_opportunities_by_relevance_list(sso_session_id, search_term)
    if results.status_code == 200:
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


def ccce_headers():
    return {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
        'Authorization': settings.COMMODITY_SEARCH_TOKEN,
    }


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
        headers=ccce_headers(),
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
        headers=ccce_headers(),
    )
    response.raise_for_status()
    return response.json()


def ccce_import_schedule(hs_code, origin_country='GB', destination_country='CA'):
    url = f'{settings.CCCE_IMPORT_SCHEDULE_URL}/{hs_code}/{origin_country}/{destination_country}/'
    response = requests.get(url=url, headers=ccce_headers())
    response.raise_for_status()
    return response.json()


@functools.lru_cache(maxsize=None)
def get_popular_export_destinations(sector_label):
    export_destinations = Counter()
    with open(settings.ROOT_DIR + 'core/fixtures/countries-sectors-export.csv', 'r') as f:
        for row in csv.DictReader(StringIO(f.read()), delimiter=','):
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


def millify(n):
    n = float(n)
    mill_names = ['', ' thousand', ' million', ' billion', ' trillion']
    mill_idx = max(0, min(len(mill_names) - 1, int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3))))
    return '{0:.2f}{unit}'.format(n / 10 ** (3 * mill_idx), unit=mill_names[mill_idx])


def process_country_imports(year_rows, from_uk=False):
    out = {}
    year_rows.sort(key=lambda row: row.get('year'), reverse=True)
    for row in year_rows:
        if row.get('uk_or_world') == ('GBR' if from_uk else 'WLD'):
            if not out:
                out = {'trade_value_raw': float(row.get('trade_value')), 'year': row.get('year')}
            else:
                # if the previous value is one year earlier
                if int(out['year']) - int(row.get('year')) == 1:
                    val = out['trade_value_raw']
                    last_val = float(row.get('trade_value'))
                    out['year_on_year_change'] = 100 * (val - last_val) / last_val
                    out['last_year'] = row.get('year')
                    out['last_value'] = row.get('trade_value')
                break
    return out


def get_comtrade_data(countries_list, commodity_code, with_country_data=True):
    response_data = {}
    comtrade_data = api_client.dataservices.get_last_year_import_data_by_country(
        countries=countries_list, commodity_code=commodity_code
    ).json()
    for country in countries_list:
        response_data[country] = {
            'import_from_world': process_country_imports(comtrade_data.get(country, []), from_uk=False),
            'import_from_uk': process_country_imports(comtrade_data.get(country, []), from_uk=True),
        }
    return response_data


def get_trade_barrier_data(countries_list, sectors_list):
    response = api_client.dataservices.get_trade_barriers(countries=countries_list, sectors=sectors_list)
    return response.json()


def get_country_data(countries, fields):
    response = api_client.dataservices.get_country_data_by_country(countries=countries, fields=fields)
    return response.json()


def build_social_link(template, request, title):
    text_to_encode = 'Export Readiness - ' + title + ' '
    return template.format(
        url=request.build_absolute_uri(),
        text=urllib.parse.quote(text_to_encode),
    )


def build_twitter_link(request, title):
    template = 'https://twitter.com/intent/tweet?text={text}{url}'
    return build_social_link(template, request, title)


def build_facebook_link(request, title):
    # note that the 'title' is not used
    template = 'https://www.facebook.com/share.php?u={url}'
    return build_social_link(template, request, title)


def build_linkedin_link(request, title):
    template = 'https://www.linkedin.com/shareArticle?mini=true&url={url}&title={text}&source=LinkedIn'
    return build_social_link(template, request, title)


def build_email_link(request, title):
    template = 'mailto:?body={url}&subject={text}'
    return build_social_link(template, request, title)


def build_social_links(request, title):
    kwargs = {'request': request, 'title': title}
    return {
        'facebook': build_facebook_link(**kwargs),
        'twitter': build_twitter_link(**kwargs),
        'linkedin': build_linkedin_link(**kwargs),
        'email': build_email_link(**kwargs),
    }


def get_trading_blocs_by_country(iso2):
    response = api_client.dataservices.trading_blocs_by_country(iso2=iso2)
    response.raise_for_status()
    return response.json()


def get_trading_blocs_name(iso2):
    trading_blocs = get_trading_blocs_by_country(iso2)
    return [item['trading_bloc_name'] for item in trading_blocs if item]


def get_file_from_s3(bucket, key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID_DATA_SCIENCE,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE,
        region_name=settings.AWS_S3_REGION_NAME_DATA_SCIENCE,
    )
    file_object = s3.get_object(Bucket=bucket, Key=key)
    return file_object


def get_s3_file_stream(file_name, bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE):
    s3_resource = get_file_from_s3(bucket_name, file_name)
    return s3_resource['Body'].read().decode('utf-8')


def retrieve_regional_offices(postcode):
    response = api_client.exporting.lookup_regional_offices_by_postcode(postcode)
    response.raise_for_status()
    return response.json()


def retrieve_regional_office_email(postcode):
    try:
        office_details = retrieve_regional_offices(postcode)
    except requests.exceptions.RequestException:
        email = None
    else:
        matches = [office for office in office_details if office['is_match']]
        email = matches[0]['email'] if matches else None
    return email


class GeoLocationRedirector:
    DOMESTIC_COUNTRY_CODES = ['GB', 'IE']
    COUNTRY_TO_LANGUAGE_MAP = {
        'CN': 'zh-hans',
        'DE': 'de',
        'ES': 'es',
        'JP': 'ja',
    }
    COOKIE_NAME = 'disable_geoloaction'
    LANGUAGE_PARAM = 'lang'

    def __init__(self, request):
        self.request = request

    @cached_property
    def country_code(self):
        client_ip, is_routable = get_client_ip(self.request)
        if client_ip and is_routable:
            try:
                response = GeoIP2().country(client_ip)
            except GeoIP2Exception:
                pass
            else:
                return response['country_code']

    @property
    def country_language(self):
        return self.COUNTRY_TO_LANGUAGE_MAP.get(self.country_code, settings.LANGUAGE_CODE)

    @property
    def should_redirect(self):
        return (
            self.COOKIE_NAME not in self.request.COOKIES  # noqa: W503
            and self.LANGUAGE_PARAM not in self.request.GET  # noqa: W503
            and self.country_code is not None  # noqa: W503
            and self.country_code not in self.DOMESTIC_COUNTRY_CODES  # noqa: W503
        )

    def get_response(self):
        params = self.request.GET.dict()
        params[self.LANGUAGE_PARAM] = self.country_language
        url = '{url}?{querystring}'.format(url='/international/', querystring=urllib.parse.urlencode(params))
        response = redirect(url)
        response.set_cookie(
            key=self.COOKIE_NAME,
            value='true',
            max_age=settings.LANGUAGE_COOKIE_AGE,
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
        )
        return response


# Rate limit by using Django sessions. Set how many click per seconds can be done.
def is_rate_limit(request, time_in_seconds, number_of_clicks):
    # Rate settings for this route.
    request.session.setdefault('rate_time_count', time.time())
    request.session.setdefault('click_numbers', 0)

    session_click_n = request.session['click_numbers']
    session_rate_time = request.session['rate_time_count']

    time_rate_passed = time.time() - session_rate_time
    request.session['click_numbers'] += 1

    # n max limtit rate per x seconds
    if time_rate_passed >= time_in_seconds:
        del request.session['rate_time_count']
        del request.session['click_numbers']

    if session_click_n >= number_of_clicks:
        return True

    return False
