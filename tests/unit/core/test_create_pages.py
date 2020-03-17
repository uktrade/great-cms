import pytest
from django.core.management import call_command
from wagtail_factories import PageFactory, SiteFactory

from domestic.models import DomesticHomePage
from exportplan.models import ExportPlanPage, ExportPlanDashboardPage


@pytest.mark.django_db
def test_create_pages(client, root_page):
    # re-create the same pages and site structure wagtail does
    welcome_page = PageFactory(parent=root_page)
    site = SiteFactory(
        id=1, root_page=welcome_page, hostname=client._base_environ()['SERVER_NAME']
    )

    call_command('create_pages')

    homepage = DomesticHomePage.objects.get()
    exportplan = ExportPlanPage.objects.get()
    exportplan_dashboard = ExportPlanDashboardPage.objects.get()

    site.refresh_from_db()

    assert site.root_page.specific == homepage
    assert homepage.get_url() == '/'
    assert exportplan.get_url() == '/export-plan/'
    assert exportplan_dashboard.get_url() == '/export-plan/dashboard/'

    assert client.get(homepage.get_url()).status_code == 200
    assert client.get(exportplan.get_url()).status_code == 200
    assert client.get(exportplan_dashboard.get_url()).status_code == 200
