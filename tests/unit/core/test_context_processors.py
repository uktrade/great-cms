import pytest
from django.shortcuts import reverse
from django.test import override_settings


@pytest.mark.django_db
def test_support_email_exists_in_template_context(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert 'great_support_email' in response.context
    assert response.context['great_support_email'] == 'great.support@trade.gov.uk'


@pytest.mark.django_db
def test_dit_link_exists_in_template_context(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert 'dit_on_govuk' in response.context
    assert response.context['dit_on_govuk'] == 'www.gov.uk/government/organisations/department-for-international-trade'


@pytest.mark.django_db
@override_settings(BREADCRUMBS_ROOT_URL='https://example.com/')
def test_migration_migration_support_vars(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert 'great_support_email' in response.context
    assert response.context['BREADCRUMBS_ROOT_URL'] == 'https://example.com/'
    assert 'FEATURE_SHOW_REPORT_BARRIER_CONTENT' in response.context
    assert 'FEATURE_SHOW_MAGNA_LINKS_IN_HEADER' in response.context
    assert 'FEATURE_SHOW_INTERNATIONAL_FOOTER_LINK' in response.context


@pytest.mark.django_db
def test_cms_slug_urls(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert response.context['DASHBOARD_URL'] == '/dashboard/'


@pytest.mark.django_db
def test_analytics_vars(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert 'GOOGLE_TAG_MANAGER_ID' in response.context
    assert 'GOOGLE_TAG_MANAGER_ENV' in response.context
    assert 'UTM_COOKIE_DOMAIN' in response.context


@pytest.mark.django_db
def test_cookie_management_vars(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert 'PRIVACY_COOKIE_DOMAIN' in response.context
