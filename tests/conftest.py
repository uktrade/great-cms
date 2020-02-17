import pytest
from unittest import mock

from django.contrib.auth import get_user_model
from wagtail.core.models import Page
from wagtail_factories import SiteFactory, PageFactory

from tests.domestic import factories
from tests.helpers import create_response


@pytest.fixture
def root_page():
    """
    On start Wagtail provides one page with ID=1 and it's called "Root page"
    """
    Page.objects.all().delete()
    return PageFactory(title='root', slug='root')


@pytest.fixture
def domestic_homepage(root_page):
    return factories.DomesticHomePageFactory.create(title='homepage', parent=root_page, live=True)


@pytest.fixture
def domestic_site(domestic_homepage):
    return SiteFactory(root_page=domestic_homepage)


@pytest.fixture
def user():
    SSOUser = get_user_model()
    import pdb
    pdb.set_trace()
    return SSOUser(
        id=1,
        pk=1,
        email='jim@example.com',
        session_id='123',
        has_user_profile=False,
    )


@pytest.fixture
def client(client, auth_backend, settings):
    def force_login(user):
        client.cookies[settings.SSO_SESSION_COOKIE] = '123'
        if user.has_user_profile:
            user_profile = {
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        else:
            user_profile = {}
        auth_backend.return_value = create_response({
            'id': user.id,
            'email': user.email,
            'hashed_uuid': user.hashed_uuid,
            'user_profile': user_profile
        })
    client.force_login = force_login
    return client


@pytest.fixture(autouse=True)
def auth_backend():
    patch = mock.patch(
        'directory_sso_api_client.sso_api_client.user.get_session_user',
        return_value=create_response(404)
    )
    yield patch.start()
    patch.stop()