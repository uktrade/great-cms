import csv
import functools
import json
import math
import os
import re
import urllib
import urllib.parse as urlparse
from collections import Counter
from difflib import SequenceMatcher
from io import StringIO
from itertools import chain
from logging import getLogger
from operator import itemgetter
from pathlib import Path

import boto3
import great_components.helpers
import requests
import sentry_sdk
from botocore.exceptions import ClientError
from directory_forms_api_client import actions
from django.conf import settings
from django.contrib.gis.geoip2 import GeoIP2, GeoIP2Exception
from django.contrib.humanize.templatetags.humanize import intword
from django.core.management import call_command
from django.http import HttpRequest
from django.shortcuts import redirect
from django.utils.encoding import iri_to_uri
from django.utils.functional import cached_property
from django.utils.http import url_has_allowed_host_and_scheme
from geoip2.errors import GeoIP2Error
from hashids import Hashids
from wagtail.models import Site

from core.constants import (
    EXPORT_SUPPORT_CATEGORIES,
    TEMPLATE_TAGS,
    TRADE_BARRIERS_BY_MARKET,
    TRADE_BARRIERS_BY_SECTOR,
)
from core.models import HCSAT, CuratedListPage
from core.serializers import parse_opportunities
from directory_api_client import api_client
from directory_constants import choices, company_types
from directory_sso_api_client import sso_api_client

USER_LOCATION_CREATE_ERROR = 'Unable to save user location'
USER_LOCATION_DETERMINE_ERROR = 'Unable to determine user location'
MALE = 'xy'
FEMALE = 'xx'

logger = getLogger(__name__)


def check_url_host_is_safelisted(request, query_param='next'):
    if request.GET.get(query_param):
        if url_has_allowed_host_and_scheme(request.GET.get(query_param), settings.SAFELIST_HOSTS):
            return iri_to_uri(request.GET.get(query_param))
        else:
            logger.error('Host is not on the safe list - %s', request.GET.get(query_param))
    return '/'


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
                out.append(f'{start}-{start + 4}')
            start += 5
    return out


def get_location(request):
    try:
        x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR']
        client_ip = x_forwarded_for.split(',')[-3].strip()
        city = GeoIP2().city(client_ip)

        return {
            'country': city['country_code'],
            'region': city['region'],
            'latitude': city['latitude'],
            'longitude': city['longitude'],
            'city': city['city'],
        }

    except (KeyError, IndexError, GeoIP2Exception) as e:
        sentry_sdk.capture_exception(e)


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
    INDUSTRIES = great_components.helpers.CompanyParser.INDUSTRIES

    SIC_CODES = dict(choices.SIC_CODES)

    def __init__(self, data):
        data = {**data}
        data.setdefault('expertise_products_services', {})
        data.setdefault('expertise_countries', [])
        data.setdefault('expertise_industries', [])
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

    @property
    def name(self):
        return self.data.get('company_name') or self.data.get('name', None)

    @property
    def number(self):
        # defaulted to NONE for NON-CH company
        return self.data.get('company_number') or self.data.get('number', None)

    @property
    def nature_of_business(self):
        return great_components.helpers.values_to_labels(values=self.data.get('sic_codes', []), choices=self.SIC_CODES)

    @property
    def is_in_companies_house(self):
        return self.data.get('company_type') == company_types.COMPANIES_HOUSE

    @property
    def is_identity_check_message_sent(self):
        return self.data['is_identity_check_message_sent']

    @property
    def address(self):
        address = self.data.get('registered_office_address', {})
        names = ['address_line_1', 'address_line_2', 'locality', 'postal_code']
        return ', '.join([address[name] for name in names if name in address])

    @property
    def postcode(self):
        if self.data.get('registered_office_address'):
            return self.data['registered_office_address'].get('postal_code')

    def serialize_for_template(self):
        if not self.data:
            return {}
        return {
            **self.data,
            'date_of_creation': self.date_of_creation,
            'address': self.address,
            'sectors': self.sectors_label,
            'keywords': self.keywords,
            'employees': self.employees_label,
            'expertise_industries': self.expertise_industries_label,
            'expertise_regions': self.expertise_regions_label,
            'expertise_countries': self.expertise_countries_label,
            'expertise_languages': self.expertise_languages_label,
            'has_expertise': self.has_expertise,
            'expertise_products_services': self.expertise_products_services_label,
            'is_in_companies_house': self.is_in_companies_house,
        }

    def serialize_for_form(self):
        if not self.data:
            return {}
        return {
            **self.data,
            'date_of_creation': self.date_of_creation,
            'address': self.address,
        }


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


def ccce_import_schedule(hs_code, origin_country='CA', destination_country='GB'):
    url = f'{settings.CCCE_IMPORT_SCHEDULE_URL}/{hs_code}/{origin_country}/{destination_country}/'
    response = requests.get(url=url, headers=ccce_headers())
    response.raise_for_status()
    return response.json()


@functools.lru_cache(maxsize=None)
def get_popular_export_destinations(sector_label):
    export_destinations = Counter()
    with open(settings.ROOT_DIR / 'core/fixtures/countries-sectors-export.csv', 'r') as f:
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
    try:
        x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR']
        client_ip = x_forwarded_for.split(',')[-3].strip()
        return client_ip
    except (KeyError, IndexError) as e:
        sentry_sdk.capture_exception(e)


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


def get_unit(values):
    try:
        return intword(max(values)).split(' ')[1]
    except (AttributeError, ValueError):
        return ''


def get_trade_highlights_by_country(iso2):
    response = api_client.dataservices.get_trade_highlights_by_country(iso2=iso2)

    if response.status_code != 200:
        return None

    return response.json()


def get_market_trends_by_country(iso2):
    response = api_client.dataservices.get_market_trends_by_country(iso2=iso2)

    if response.status_code != 200:
        return None

    api_data = response.json()

    if api_data['data']:
        for record in api_data['data']:
            record['total'] = record['imports'] + record['exports']

        totals = [x['total'] for x in api_data['data']]
        api_data['metadata']['unit'] = get_unit(totals)

    return api_data


def process_top_exports(response):
    if response.status_code != 200:
        return None

    api_data = response.json()

    if api_data['data']:
        values = [x['value'] for x in api_data['data']]
        max_value = max(values)

        api_data['metadata']['unit'] = get_unit(values)

        for item in api_data['data']:
            item['percent'] = round((item['value'] / max_value) * 100, 1)

    return api_data


def get_top_goods_exports_by_country(iso2):
    response = api_client.dataservices.get_top_five_goods_by_country(iso2=iso2)

    return process_top_exports(response)


def get_top_services_exports_by_country(iso2):
    response = api_client.dataservices.get_top_five_services_by_country(iso2=iso2)

    return process_top_exports(response)


def get_economic_highlights_by_country(iso2):
    response = api_client.dataservices.get_economic_highlights_by_country(iso2=iso2)
    if response.status_code != 200:
        return None

    return response.json()


def get_stats_by_country(iso2):
    stats = {
        'highlights': get_trade_highlights_by_country(iso2=iso2),
        'market_trends': get_market_trends_by_country(iso2=iso2),
        'goods_exports': get_top_goods_exports_by_country(iso2=iso2),
        'services_exports': get_top_services_exports_by_country(iso2=iso2),
        'economic_highlights': get_economic_highlights_by_country(iso2=iso2),
    }

    stats = {k: v for k, v in stats.items() if v and v['data']}
    return stats or None


def get_country_data(countries, fields):
    response = api_client.dataservices.get_country_data_by_country(countries=countries, fields=fields)
    return response.json()


def get_markets_list():
    try:
        response = api_client.dataservices.get_markets_data()
    except Exception:
        return choices.COUNTRY_CHOICES
    if not response.ok:
        return choices.COUNTRY_CHOICES
    json_data = response.json()
    if len(json_data) == 0:
        return choices.COUNTRY_CHOICES
    market_list = []
    for market in json_data:
        if market['enabled']:
            market_list.append((market['iso2_code'], market['name']))
    market_list.sort(key=itemgetter(1))
    return market_list


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
    kwargs = {}
    if hasattr(settings, 'AWS_ACCESS_KEY_ID_DATA_SCIENCE') and hasattr(settings, 'AWS_SECRET_ACCESS_KEY_DATA_SCIENCE'):
        kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID_DATA_SCIENCE
        kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY_DATA_SCIENCE
    s3 = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME_DATA_SCIENCE,
        **kwargs,
    )
    file_object = s3.get_object(Bucket=bucket, Key=key)
    return file_object


def get_s3_file_stream(file_name, bucket_name=settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE):
    s3_resource = get_file_from_s3(bucket_name, file_name)
    return s3_resource['Body'].read().decode('utf-8')


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
        # Find x-forwarded-for
        try:
            x_forwarded_for = self.request.META['HTTP_X_FORWARDED_FOR']
            client_ip = x_forwarded_for.split(',')[-3].strip()
            response = GeoIP2().country(client_ip)
            return response['country_code']
        except (KeyError, IndexError, GeoIP2Exception, GeoIP2Error) as e:
            sentry_sdk.capture_exception(e)

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


hashids = Hashids(settings.HASHIDS_SALT, min_length=8)


def h_encrypt(id):
    return hashids.encrypt(id)


def h_decrypt(h):
    z = hashids.decrypt(h)
    if z:
        return z[0]


class HashIdConverter:
    regex = '[a-zA-Z0-9]{8,}'

    def to_python(self, value):
        return h_decrypt(value)

    def to_url(self, value):
        return h_encrypt(value)


class ClamAvClient:
    auth = requests.auth.HTTPBasicAuth(
        settings.CLAM_AV_USERNAME,
        settings.CLAM_AV_PASSWORD,
    )
    base_url = settings.CLAM_AV_HOST
    endpoints = {'scan-chunked': {'path': 'v2/scan-chunked', 'headers': {'Transfer-encoding': 'chunked'}}}

    def post(self, endpoint, data):
        url = urlparse.urljoin(self.base_url, endpoint['path'])
        return requests.post(
            url,
            auth=self.auth,
            headers=endpoint.get('headers'),
            data=data,
        )

    def chunk_gen(self, file):
        for chunk in file.chunks():
            yield chunk

    def scan_chunked(self, file):
        return self.post(self.endpoints['scan-chunked'], self.chunk_gen(file))


clam_av_client = ClamAvClient()


def send_campaign_site_review_reminder(email_list, site_name, review_days, review_link):
    campaign_email = settings.MODERATION_EMAIL_DIST_LIST
    for recipient in email_list:
        action = actions.GovNotifyEmailAction(
            email_address=recipient,
            template_id=settings.CAMPAIGN_SITE_REVIEW_REMINDER_TEMPLATE_ID,
            email_reply_to_id=settings.CAMPAIGN_MODERATION_REPLY_TO_ID,
            form_url=str(),
        )
        data = {
            'campaign_email': campaign_email,
            'site_name': site_name,
            'review_days': review_days,
            'review_link': review_link,
        }
        response = action.save(data)
        response.raise_for_status()


def _get_s3_client_kwargs():
    kwargs = {}
    if hasattr(settings, 'AWS_ACCESS_KEY_ID') and hasattr(settings, 'AWS_SECRET_ACCESS_KEY'):
        kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID
        kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY

    return kwargs


def upload_file_to_s3(file_name: str, object_name: str):
    # dont upload files if running in circleci
    if settings.IS_CIRCLECI_ENV:
        return
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        **_get_s3_client_kwargs(),
    )
    try:
        s3_client.upload_file(file_name, settings.AWS_STORAGE_BUCKET_NAME, object_name)
    except ClientError as ce:
        logger.error(ce)


def geoip_file_exists_in_s3(object_name: str):
    s3 = boto3.resource('s3')
    try:
        s3.Object(settings.AWS_STORAGE_BUCKET_NAME, object_name).load()
    except ClientError:
        return False
    else:
        return True


def delete_existing_geoip_files():
    country = f'{settings.GEOIP_PATH}/{settings.GEOIP_COUNTRY}'
    city = f'{settings.GEOIP_PATH}/{settings.GEOIP_CITY}'
    file = Path(country)
    if file.exists():
        os.remove(country)
    file = Path(city)
    if file.exists():
        os.remove(city)


def download_geoip_files_from_s3():
    # dont download files if running in circleci
    if settings.IS_CIRCLECI_ENV:
        return

    if geoip_file_exists_in_s3(f'geoip_data/{settings.GEOIP_COUNTRY}') and geoip_file_exists_in_s3(
        f'geoip_data/{settings.GEOIP_CITY}'
    ):
        try:
            delete_existing_geoip_files()
        except IOError:
            pass
        else:
            s3_client = boto3.client(
                's3',
                region_name=settings.AWS_S3_REGION_NAME,
                **_get_s3_client_kwargs(),
            )
            s3_client.download_file(
                settings.AWS_STORAGE_BUCKET_NAME,
                f'geoip_data/{settings.GEOIP_CITY}',
                f'{settings.GEOIP_PATH}/{settings.GEOIP_CITY}',
            )
            s3_client.download_file(
                settings.AWS_STORAGE_BUCKET_NAME,
                f'geoip_data/{settings.GEOIP_COUNTRY}',
                f'{settings.GEOIP_PATH}/{settings.GEOIP_COUNTRY}',
            )
    else:
        try:
            call_command('download_geolocation_data')
        except Exception:
            logger.exception('Failed to  download GeoIP data')


def product_picker(product):
    response = requests.get(
        f'https://www.trade-tariff.service.gov.uk/api/v2/search_references.json?query[letter]={product}', timeout=4
    )
    response.raise_for_status()
    return response.json()


def hcsat_get_initial(model, csat_id):
    if csat_id:
        csat_record = model.objects.get(id=csat_id)
        satisfaction = csat_record.satisfaction_rating
        if satisfaction:
            return {'satisfaction': satisfaction}
    else:
        return {'satisfaction': ''}


def mapped_categories(form_data):
    categories = EXPORT_SUPPORT_CATEGORIES
    market = form_data.get('market')
    is_goods = form_data.get('exporter_type') == 'goods'
    is_service = form_data.get('exporter_type') == 'service'
    query_string = '?is_guided_journey=True'

    if market:
        query_string += f'&market={market}'

    if is_goods:
        query_string += f'&is_goods={is_goods}'

    if is_service:
        query_string += f'&is_service={is_service}'

    if form_data.get('exporter_type') == 'service':
        categories = [(url, label, query_string) for url, label in categories if label != 'Logistics']
    else:
        categories = [(url, label, query_string) for url, label in categories]

    return categories


def get_trade_barrier_count(market, sector):
    trade_barriers_by_market = TRADE_BARRIERS_BY_MARKET
    trade_barriers_by_sector = TRADE_BARRIERS_BY_SECTOR

    if market:
        if trade_barriers_by_market.get(market):
            return trade_barriers_by_market.get(market)

    if sector:
        if trade_barriers_by_sector.get(sector):
            return trade_barriers_by_sector.get(sector)

    return None


def get_ukea_events(all_events, market, sector):
    events = all_events.filter(
        closed=False, country_tags__isnull=True, sector_tags__isnull=True, region_tags__isnull=True
    )
    market = str(market or '')
    sector = str(sector or '')

    if market != '' and sector != '':
        events = list(
            chain(
                all_events.filter(
                    closed=False, country_tags__name__contains=str(market), sector_tags__name__contains=str(sector)
                ),
                all_events.filter(closed=False, country_tags__isnull=True, sector_tags__name__contains=str(sector)),
                all_events.filter(closed=False, country_tags__name__contains=str(market), sector_tags__isnull=True),
                events,
            )
        )

    if market != '' and sector == '':
        events = list(
            chain(
                all_events.filter(closed=False, country_tags__name__contains=str(market), sector_tags__isnull=True),
                all_events.filter(
                    closed=False,
                    country_tags__name__contains=str(market),
                    sector_tags__isnull=False,
                ),
                events,
            )
        )

    if sector != '' and market == '':
        events = list(
            chain(
                all_events.filter(closed=False, country_tags__isnull=True, sector_tags__name__contains=str(sector)),
                all_events.filter(closed=False, country_tags__isnull=False, sector_tags__name__contains=str(sector)),
                events,
            )
        )

    return events[:2]


def get_sectors_and_sic_sectors_file():
    json_data = open('core/fixtures/sectors-and-sic-sectors.json')
    deserialised_data = json.load(json_data)
    json_data.close()
    return deserialised_data


def send_hcsat_feedback(data: HCSAT) -> None:
    action = actions.HCSatAction(
        form_url=str(),
    )
    response = action.save(data)
    response.raise_for_status()


def is_bgs_site(root_url: str) -> bool:
    sentry_sdk.capture_message(f'BGS_SITE: {settings.BGS_SITE} match root_url: {root_url}')
    return settings.BGS_SITE in root_url


def is_bgs_site_from_request(request: HttpRequest) -> bool:
    site = Site.find_for_request(request)
    return is_bgs_site(site.root_url)


def get_template_id(template_tag):
    return TEMPLATE_TAGS[settings.FEATURE_USE_BGS_TEMPLATES][template_tag]
