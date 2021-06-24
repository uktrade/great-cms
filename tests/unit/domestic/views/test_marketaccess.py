from unittest import mock

import pytest
from django.conf import settings
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_form_feature_flag_off(client, settings):
    settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT = False

    response = client.get(reverse('domestic:market-access'))

    assert response.status_code == 404


def test_form_feature_flag_on(client, settings):
    settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT = True

    response = client.get(reverse('domestic:market-access'))

    assert response.status_code == 200


def test_error_box_at_top_of_page_shows(client):
    settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT = True
    url_name = 'domestic:report-ma-barrier'
    view_name = 'report_market_access_barrier_form_view'

    response = client.post(
        reverse(url_name, kwargs={'step': 'about'}),
        {
            view_name + '-current_step': 'about',
            'about-firstname': '',
            'about-lastname': '',
            'about-jobtitle': '',
            'about-business_type': '',
            'about-company_name': '',
            'about-email': '',
            'about-phone': '',
        },
    )
    assert response.status_code == 200
    assert 'error-message-box' in str(response.content)


@mock.patch('directory_forms_api_client.actions.ZendeskAction')
def test_form_submission(mock_zendesk_action, client):
    settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT = True
    url_name = 'domestic:report-ma-barrier'
    view_name = 'report_market_access_barrier_form_view'
    business_type = 'I’m an exporter or investor, or I want to export or invest'

    response = client.post(
        reverse(url_name, kwargs={'step': 'about'}),
        {
            view_name + '-current_step': 'about',
            'about-firstname': 'Craig',
            'about-lastname': 'Smith',
            'about-jobtitle': 'Musician',
            'about-business_type': business_type,
            'about-company_name': 'Craig Music',
            'about-email': 'craig@example.com',
            'about-phone': '0123456789',
        },
    )
    assert response.status_code == 302
    assert response.url == reverse(url_name, kwargs={'step': 'problem-details'})
    response = client.get(response.url)
    assert response.status_code == 200

    response = client.post(
        reverse(url_name, kwargs={'step': 'problem-details'}),
        {
            view_name + '-current_step': 'problem-details',
            'problem-details-product_service': 'something',
            'problem-details-location': 'AO',
            'problem-details-problem_summary': 'problem summary',
            'problem-details-impact': 'problem impact',
            'problem-details-resolve_summary': 'steps in resolving',
            'problem-details-problem_cause': ['covid-19'],
        },
    )
    assert response.status_code == 302
    assert response.url == reverse(url_name, kwargs={'step': 'summary'})
    response = client.get(response.url)
    assert response.status_code == 200

    response = client.post(
        reverse(url_name, kwargs={'step': 'summary'}),
        {
            view_name + '-current_step': 'summary',
        },
    )
    assert response.status_code == 302
    assert response.url == reverse(url_name, kwargs={'step': 'finished'})
    response = client.get(response.url)
    assert response.status_code == 200

    assert mock_zendesk_action.call_count == 1
    subject = f'{settings.MARKET_ACCESS_ZENDESK_SUBJECT}: AO: Craig Music'
    assert mock_zendesk_action.call_args == mock.call(
        subject=subject,
        full_name='Craig Smith',
        email_address='craig@example.com',
        service_name='market_access',
        subdomain='debug',
        form_url=reverse(url_name, kwargs={'step': 'about'}),
        sender={
            'email_address': 'craig@example.com',
            'country_code': None,
            'ip_address': None,
        },
    )
    assert mock_zendesk_action().save.call_count == 1
    assert mock_zendesk_action().save.call_args == mock.call(
        {
            'firstname': 'Craig',
            'lastname': 'Smith',
            'jobtitle': 'Musician',
            'business_type': business_type,
            'other_business_type': '',
            'company_name': 'Craig Music',
            'email': 'craig@example.com',
            'phone': '0123456789',
            'product_service': 'something',
            'location': 'AO',
            'location_label': 'Angola',
            'problem_summary': 'problem summary',
            'impact': 'problem impact',
            'resolve_summary': 'steps in resolving',
            'problem_cause': ['covid-19'],
            'problem_cause_label': ['Covid-19'],
            'contact_by_email': False,
            'contact_by_phone': False,
        }
    )


def test_form_initial_data(client):
    settings.FEATURE_SHOW_REPORT_BARRIER_CONTENT = True
    response_one = client.get(
        reverse(
            'domestic:report-ma-barrier',
            kwargs={'step': 'about'},
        ),
    )
    assert response_one.context_data['form'].initial == {}

    response_two = client.get(
        reverse(
            'domestic:report-ma-barrier',
            kwargs={'step': 'problem-details'},
        ),
    )
    assert response_two.context_data['form'].initial == {}
