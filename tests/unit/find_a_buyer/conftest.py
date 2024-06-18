import http
from copy import deepcopy
from unittest.mock import patch

import pytest
import requests

from directory_api_client.client import api_client


@pytest.fixture
def retrieve_supplier_profile_data():
    return {
        'company': 1,
        'company_email': 'test@example.com',
        'sso_id': 1,
        'is_company_owner': True,
    }


@pytest.fixture
def retrieve_profile_data():
    return {
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'country': 'GB',
        'date_of_creation': '2015-03-02',
        'description': 'Ecommerce website',
        'email_address': 'test@example.com',
        'email_full_name': 'Jeremy',
        'employees': '501-1000',
        'facebook_url': 'http://www.facebook.com',
        'has_valid_address': True,
        'is_published': True,
        'is_verification_letter_sent': False,
        'keywords': 'word1, word2',
        'linkedin_url': 'http://www.linkedin.com',
        'locality': 'London',
        'logo': 'nice.jpg',
        'mobile_number': '07507694377',
        'modified': '2016-11-23T11:21:10.977518Z',
        'name': 'Great company',
        'number': 123456,
        'po_box': '',
        'postal_code': 'E14 6XK',
        'postal_full_name': 'Jeremy',
        'sectors': ['SECURITY'],
        'summary': 'good',
        'supplier_case_studies': [],
        'twitter_url': 'http://www.twitter.com',
        'verified_with_code': True,
        'verified_with_companies_house_oauth2': False,
        'verified_with_preverified_enrolment': False,
        'is_verified': True,
        'website': 'http://example.com',
    }


@pytest.fixture
def company_profile_companies_house_data():
    return {
        'email_full_name': 'Jeremy Companies House',
        'email_address': 'test@example.com',
        'postal_full_name': 'Jeremy',
        'address_line_1': '123 Fake Street',
        'address_line_2': 'Fakeville',
        'locality': 'London',
        'postal_code': 'E14 6XK',
        'po_box': '',
        'country': 'GB',
    }


@pytest.fixture
def api_response_supplier_profile_200(retrieve_supplier_profile_data):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy(retrieve_supplier_profile_data)
    return response


@pytest.fixture
def api_response_company_profile_companies_house_200(company_profile_companies_house_data):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy(company_profile_companies_house_data)
    return response


@pytest.fixture
def api_response_company_profile_200(retrieve_profile_data):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy(retrieve_profile_data)
    return response


@pytest.fixture
def api_response_company_profile_unverified_200(retrieve_profile_data):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: {**retrieve_profile_data, 'is_verified': False}
    return response


@pytest.fixture
def api_response_company_profile_letter_sent_200(retrieve_profile_data):
    profile_data = deepcopy(retrieve_profile_data)
    profile_data['is_verification_letter_sent'] = True
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: profile_data
    return response


@pytest.fixture
def api_response_200():
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: deepcopy({})
    return response


@pytest.fixture(autouse=True)
def retrieve_profile(api_response_company_profile_200):
    stub = patch.object(
        api_client.company,
        'profile_retrieve',
        return_value=api_response_company_profile_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture
def retrieve_profile_unverified(api_response_company_profile_unverified_200):
    stub = patch.object(
        api_client.company,
        'profile_retrieve',
        return_value=api_response_company_profile_unverified_200,
    )
    stub.start()
    yield
    stub.stop()


@pytest.fixture(autouse=True)
def retrieve_supplier_profile(api_response_supplier_profile_200):
    stub = patch.object(
        api_client.supplier,
        'retrieve_profile',
        return_value=api_response_supplier_profile_200,
    )
    stub.start()
    yield
    stub.stop()
