from profile.exops import views
from profile.exops.helpers import exopps_client
from unittest.mock import Mock, patch

from django.urls import reverse

from core.tests.helpers import create_response


def response_factory(status_code):
    return Mock(return_value=create_response(status_code=status_code))


@patch.object(exopps_client, 'get_exops_data', response_factory(200))
def test_export_opportunities_applications_exposes_context(client, settings, user):
    client.force_login(user)
    settings.EXPORTING_OPPORTUNITIES_SEARCH_URL = 'http://find'

    response = client.get(reverse('export-opportunities-applications'))
    context_data = response.context_data

    assert context_data['exops_tab_classes'] == 'active'
    assert context_data['EXPORTING_OPPORTUNITIES_SEARCH_URL'] == 'http://find'


@patch.object(exopps_client, 'get_exops_data', response_factory(200))
def test_export_opportunities_email_alerts_exposes_context(client, settings, user):
    client.force_login(user)
    settings.EXPORTING_OPPORTUNITIES_SEARCH_URL = 'http://find'

    response = client.get(reverse('export-opportunities-email-alerts'))
    context_data = response.context_data

    assert context_data['exops_tab_classes'] == 'active'
    assert context_data['EXPORTING_OPPORTUNITIES_SEARCH_URL'] == 'http://find'


def test_opportunities_applications_unauthenticated(client):
    response = client.get(reverse('export-opportunities-applications'))

    assert response.status_code == 302


def test_opportunities_email_alerts_unauthenticated(client):
    response = client.get(reverse('export-opportunities-email-alerts'))

    assert response.status_code == 302


@patch.object(exopps_client, 'get_exops_data', response_factory(403))
def test_opportunities_applications_retrieve_not_found(client, user):
    client.force_login(user)

    response = client.get(reverse('export-opportunities-applications'))

    assert response.template_name == [views.ExportOpportunitiesApplicationsView.template_name_not_exops_user]


@patch.object(exopps_client, 'get_exops_data', response_factory(200))
def test_opportunities_applications_retrieve_found(client, user):
    client.force_login(user)

    response = client.get(reverse('export-opportunities-applications'))

    assert response.template_name == [views.ExportOpportunitiesApplicationsView.template_name_exops_user]


@patch.object(exopps_client, 'get_exops_data', response_factory(500))
def test_opportunities_applications_retrieve_error(client, user):
    client.force_login(user)

    response = client.get(reverse('export-opportunities-applications'))

    assert response.template_name == [views.ExportOpportunitiesApplicationsView.template_name_error]


@patch.object(exopps_client, 'get_exops_data', response_factory(403))
def test_opportunities_email_alerts_retrieve_not_found(client, user):
    client.force_login(user)

    response = client.get(reverse('export-opportunities-email-alerts'))

    assert response.template_name == [views.ExportOpportunitiesEmailAlertsView.template_name_not_exops_user]


@patch.object(exopps_client, 'get_exops_data', response_factory(200))
def test_opportunities_email_alerts_retrieve_found(client, user):
    client.force_login(user)

    response = client.get(reverse('export-opportunities-email-alerts'))

    assert response.template_name == [views.ExportOpportunitiesEmailAlertsView.template_name_exops_user]


@patch.object(exopps_client, 'get_exops_data', response_factory(500))
def test_opportunities_email_alerts_retrieve_error(client, user):
    client.force_login(user)

    response = client.get(reverse('export-opportunities-email-alerts'))

    assert response.template_name == [views.ExportOpportunitiesEmailAlertsView.template_name_error]
