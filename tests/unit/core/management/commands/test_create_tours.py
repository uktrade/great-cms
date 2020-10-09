import pytest
from io import StringIO
from django.core.management import call_command

from core import models


@pytest.mark.django_db
def test_create_tours(
    client, domestic_homepage, exportplan_dashboard, domestic_site, user, mock_get_company_profile
):
    mock_get_company_profile.return_value = {'name': 'Example company'}

    call_command('create_tours', stdout=StringIO())

    domestic_homepage.refresh_from_db()
    exportplan = models.ListPage.objects.get(slug='export-plan')

    assert domestic_homepage.get_url() == '/'
    assert exportplan.get_url() == '/export-plan/'
    assert exportplan_dashboard.get_url() == '/export-plan/dashboard/'

    assert client.get(domestic_homepage.get_url()).status_code == 200

    client.force_login(user)

    assert client.get(exportplan.get_url()).status_code == 200
    assert client.get(exportplan_dashboard.get_url()).status_code == 200
