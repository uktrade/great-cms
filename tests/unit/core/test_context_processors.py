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
