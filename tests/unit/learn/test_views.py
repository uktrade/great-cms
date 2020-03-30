import pytest
from tests.unit.learn.factories import LearnPageFactory


@pytest.mark.django_db
def test_learn_page(client, domestic_site):
    page = LearnPageFactory(parent=domestic_site, slug='learn')
    response = client.get(page.url)
    assert response.status_code == 200
