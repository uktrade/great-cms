from unittest import mock

from django.contrib.auth.models import AnonymousUser

from core import helpers, middleware


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
