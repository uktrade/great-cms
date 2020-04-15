import pytest
from io import StringIO
from django.core.management import call_command

from core import models


@pytest.mark.django_db
def test_create_pages(client, domestic_homepage, domestic_site):

    call_command('create_pages', stdout=StringIO())

    domestic_homepage.refresh_from_db()
    exportplan = models.ListPage.objects.get(slug='export-plan')
    exportplan_dashboard = models.DetailPage.objects.get(slug='dashboard')

    assert domestic_homepage.get_url() == '/'
    assert exportplan.get_url() == '/export-plan/'
    assert exportplan_dashboard.get_url() == '/export-plan/dashboard/'

    assert client.get(domestic_homepage.get_url()).status_code == 200
    assert client.get(exportplan.get_url()).status_code == 200
    assert client.get(exportplan_dashboard.get_url()).status_code == 200
