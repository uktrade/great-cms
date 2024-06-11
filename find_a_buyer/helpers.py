from collections import OrderedDict
from functools import partial
import logging
import urllib
from urllib.parse import urljoin
from django.conf import settings
import requests
from directory_api_client.client import api_client

MESSAGE_AUTH_FAILED = 'Auth failed with Companies House'


logger = logging.getLogger(__name__)


def has_company(sso_session_id):
    response = api_client.supplier.retrieve_profile(
        sso_session_id=sso_session_id
    )
    if response.status_code == 200:
        profile = response.json()
        has_company = bool(profile['company'])
    else:
        has_company = False

    return has_company


class CompaniesHouseClient:
    api_key = settings.COMPANIES_HOUSE_API_KEY
    client_id = settings.COMPANIES_HOUSE_CLIENT_ID
    client_secret = settings.COMPANIES_HOUSE_CLIENT_SECRET
    make_api_url = partial(urljoin, settings.COMPANIES_HOUSE_API_URL)
    make_oauth2_url = partial(urljoin, settings.COMPANIES_HOUSE_URL)
    endpoints = {
        'profile': make_api_url('company/{number}'),
        'address': make_api_url('company/{number}/registered-office-address'),
        'search': make_api_url('search/companies'),
        'oauth2': make_oauth2_url('oauth2/authorise'),
        'oauth2-token': make_oauth2_url('oauth2/token'),
    }
    session = requests.Session()

    @classmethod
    def get_auth(cls):
        return requests.auth.HTTPBasicAuth(cls.api_key, '')

    @classmethod
    def get(cls, url, params={}):
        response = cls.session.get(url=url, params=params, auth=cls.get_auth())
        if response.status_code == 403:
            logger.error(MESSAGE_AUTH_FAILED)
        return response

    @classmethod
    def make_oauth2_url(cls, redirect_uri, company_number):
        # ordered dict to facilitate testing
        params = OrderedDict([
            ('client_id', cls.client_id),
            ('redirect_uri', redirect_uri),
            ('response_type', 'code'),
            ('scope', cls.endpoints['profile'].format(number=company_number)),
        ])
        return cls.endpoints['oauth2'] + '?' + urllib.parse.urlencode(params)

    @classmethod
    def verify_oauth2_code(cls, code, redirect_uri):
        url = cls.endpoints['oauth2-token']
        params = OrderedDict([
            ('grant_type', 'authorization_code'),
            ('code', code),
            ('client_id', cls.client_id),
            ('client_secret', cls.client_secret),
            ('redirect_uri', redirect_uri),
        ])
        return cls.session.post(url=url + '?' + urllib.parse.urlencode(params))


def get_company_profile(sso_session_id):
    response = api_client.company.profile_retrieve(sso_session_id)
    response.raise_for_status()
    return response.json()


def halt_validation_on_failure(*all_validators):
    """
    Django runs all validators on a field and shows all errors. Sometimes this
    is undesirable: we may want the validators to stop on the first error.

    """

    def inner(value):
        for validator in all_validators:
            validator(value)
    inner.inner_validators = all_validators
    return [inner]


def build_company_address(company_profile):
    field_names = [
        'address_line_1',
        'address_line_2',
        'locality',
        'country',
        'postal_code',
        'po_box',
    ]
    address_parts = []
    for field_name in field_names:
        value = company_profile.get(field_name)
        if value:
            address_parts.append(value)
    return ', '.join(address_parts)
