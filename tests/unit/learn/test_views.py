import pytest


@pytest.mark.django_db
def test_learn_landing_page(client, exportplan_homepage):
    response = client.get('/learn/')
    assert response.status_code == 200
