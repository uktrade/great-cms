import pytest
from django.core.management import call_command
from wagtail_factories import PageFactory, SiteFactory

from core.models import PersonalisedPage
from exportplan.models import ExportPlanPage, ExportPlanDashboardPage


@pytest.mark.django_db
def test_create_pages(client, domestic_homepage, domestic_site):

    call_command('create_pages')

    domestic_homepage.refresh_from_db()
    exportplan = ExportPlanPage.objects.get()
    exportplan_dashboard = ExportPlanDashboardPage.objects.get()
    country = PersonalisedPage.objects.get()

    assert domestic_homepage.get_url() == '/'
    assert exportplan.get_url() == '/export-plan/'
    assert exportplan_dashboard.get_url() == '/export-plan/dashboard/'
    assert country.get_url() == '/country/'

    assert client.get(domestic_homepage.get_url()).status_code == 200
    assert client.get(exportplan.get_url()).status_code == 200
    assert client.get(exportplan_dashboard.get_url()).status_code == 200
    assert client.get(country.get_url()).status_code == 200
