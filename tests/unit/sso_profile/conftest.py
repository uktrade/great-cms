from unittest import mock

import pytest
from django.core.cache import cache

from core.tests.helpers import create_response
from sso.models import BusinessSSOUser


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()


@pytest.fixture
def sso_user_no_profile():
    return BusinessSSOUser(
        id=1,
        pk=1,
        email='jim@example.com',
        session_id='123',
        has_user_profile=False,
    )


@pytest.fixture
def sso_user_with_profile():
    return BusinessSSOUser(
        id=1,
        pk=1,
        email='jim2@example.com',
        session_id='123',
        has_user_profile=True,
        first_name='No Name',
    )


@pytest.fixture(autouse=True)
def sso_profile_feature_flags(settings):
    # solves this issue: https://github.com/pytest-dev/pytest-django/issues/601
    settings.SSO_PROFILE_FEATURE_FLAGS = {**settings.SSO_PROFILE_FEATURE_FLAGS}
    yield settings.SSO_PROFILE_FEATURE_FLAGS


@pytest.fixture(autouse=True)
def mock_create_user_profile():
    response = create_response(
        {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'job_title': 'Director',
            'mobile_phone_number': '08888888888',
        }
    )
    patch = mock.patch('directory_sso_api_client.sso_api_client.user.create_user_profile', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_update_user_profile():
    response = create_response()
    patch = mock.patch('directory_sso_api_client.sso_api_client.user.update_user_profile', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def update_supplier_profile_name():
    response = create_response()
    patch = mock.patch('directory_api_client.api_client.supplier.profile_update', return_value=response)
    yield patch.start()
    patch.stop()
