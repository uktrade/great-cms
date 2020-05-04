from unittest import mock

import pytest

from django.contrib.auth.models import AnonymousUser

from core import helpers, middleware
from tests.unit.core import factories


@mock.patch.object(helpers, 'store_user_location')
def test_stores_user_location(mock_store_user_location, rf, user):
    request = rf.get('/')
    request.user = user

    middleware.UserLocationStoreMiddleware().process_request(request)

    assert mock_store_user_location.call_count == 1
    assert mock_store_user_location.call_args == mock.call(request)


@mock.patch.object(helpers, 'store_user_location')
def test_stores_user_location_anon_user(mock_store_user_location, rf):
    request = rf.get('/')
    request.user = AnonymousUser()

    middleware.UserLocationStoreMiddleware().process_request(request)

    assert mock_store_user_location.call_count == 0


@pytest.mark.django_db
def test_user_specific_redirect_middleware(domestic_site, client):
    learn_page = factories.ListPageFactory(parent=domestic_site.root_page, slug='learn')
    introduction_page = factories.DetailPageFactory(parent=learn_page, slug='introduction')
    categories_page = factories.DetailPageFactory(parent=learn_page, slug='categories')

    # Given the user has gone to /learn/inroduction/
    response = client.get(introduction_page.url)
    assert response.status_code == 200

    # When the user next goes to /learn/ or /learn/inroduction/
    for page in [learn_page, introduction_page]:
        response = client.get(page.url)

        # Then they should be redirected to /learn/categories/
        assert response.status_code == 302
        assert response.url == categories_page.url
