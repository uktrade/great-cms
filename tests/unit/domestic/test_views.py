import pytest
from core import constants


@pytest.mark.django_db
def test_landing_page_not_logged_in(client, user, domestic_site):
    response = client.get('/')

    assert response.status_code == 200


@pytest.mark.django_db
def test_landing_page_logged_in(client, user, domestic_site):

    client.force_login(user)
    response = client.get('/')
    assert response.status_code == 302
    assert response.url == constants.DASHBOARD_
