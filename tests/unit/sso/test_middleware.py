from unittest import mock

import pytest
from django.test import override_settings
from django.urls import reverse
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

from sso.middleware import AuthenticationMiddleware


@override_settings(LOGIN_URL='/test/login/url/')
@pytest.mark.parametrize(
    'path,expected_redirect_dest',
    (
        ('/admin/test/', '/test/login/url/'),
        (reverse('wagtailadmin_home'), '/test/login/url/'),  # Wagtail admin
        ('/django-admin/auth/user/', reverse('admin:index')),  # Django admin
        (reverse('core:contact-us-help'), reverse('core:login')),
    ),
)
def test_authentication_middleware__token_expiry(rf, path, expected_redirect_dest):

    middleware = AuthenticationMiddleware()

    request = rf.get(path)

    with mock.patch('sso.middleware.auth.authenticate') as mock_authenticate:
        mock_authenticate.side_effect = TokenExpiredError('Faked timeout')
        response = middleware.process_request(request)

        assert response.status_code == 302
        assert response._headers['location'] == ('Location', expected_redirect_dest)
