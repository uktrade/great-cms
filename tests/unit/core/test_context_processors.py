import pytest
from django.shortcuts import reverse
from django.test import override_settings
from django.utils import translation

from core import context_processors


@pytest.mark.django_db
def test_support_email_exists_in_template_context(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert 'great_support_email' in response.context
    assert response.context['great_support_email'] == 'great.support@trade.gov.uk'  # /PS-IGNORE


@pytest.mark.django_db
def test_dit_link_exists_in_template_context(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert 'dit_on_govuk' in response.context
    assert response.context['dit_on_govuk'] == 'www.gov.uk/government/organisations/department-for-business-and-trade'


@pytest.mark.django_db
@override_settings(BREADCRUMBS_ROOT_URL='https://example.com/')
def test_migration_migration_support_vars(client):
    url = reverse('core:signup')
    response = client.get(url)
    assert 'great_support_email' in response.context
    assert response.context['BREADCRUMBS_ROOT_URL'] == 'https://example.com/'
    assert 'FEATURE_SHOW_REPORT_BARRIER_CONTENT' in response.context


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


@pytest.mark.django_db
def test_directory_components_html_lang_attribute(settings):
    with translation.override('fr'):
        actual = context_processors.directory_components_html_lang_attribute(None)  # noqa

        assert actual['directory_components_html_lang_attribute'] == translation.get_language()

    with translation.override('de'):
        actual = context_processors.directory_components_html_lang_attribute(None)  # noqa

        assert actual['directory_components_html_lang_attribute'] == translation.get_language()
