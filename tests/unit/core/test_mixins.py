from unittest import mock

import pytest

from core.mixins import GetSnippetContentMixin, PrepopulateFormMixin
from domestic.models import DomesticHomePage
from sso.models import BusinessSSOUser
from tests.helpers import create_response
from tests.unit.domestic import factories


@pytest.mark.django_db
def test_wagtail_admin_exclusive_page_can_only_be_created_once(root_page):

    assert DomesticHomePage.can_create_at(root_page)
    factories.DomesticHomePageFactory(parent=root_page)
    assert DomesticHomePage.can_create_at(root_page) is False


def test_get_snippet_content_mixin():
    class TestView(GetSnippetContentMixin):
        snippet_import_path = 'path.to.models.FakeTestSnippet'
        slug = 'foo-bar-baz'

    test_view = TestView()

    assert test_view.slug == 'foo-bar-baz'
    assert test_view.snippet_import_path == 'path.to.models.FakeTestSnippet'

    mock_snippet_instance = mock.Mock(name='mock_snippet_instance')

    mock_snippet_model = mock.Mock(name='mock_snippet_model')
    mock_snippet_model.objects.get.return_value = mock_snippet_instance

    mock_module = mock.Mock(name='mock_module')
    mock_module.FakeTestSnippet = mock_snippet_model

    with mock.patch('core.mixins.import_module') as mock_import_module:
        mock_import_module.return_value = mock_module
        assert test_view.get_snippet_instance() == mock_snippet_instance

    mock_snippet_model.objects.get.assert_called_once_with(slug='foo-bar-baz')


@pytest.mark.parametrize(
    'full_name,first_name,last_name',
    (
        ('James Example', 'James', 'Example'),
        ('James', 'James', None),
        ('James Earl Jones', 'James', 'Jones'),
        ('', None, None),
    ),
)
def test_retrieve_company_profile_mixin_name_guessing(
    rf,
    full_name,
    first_name,
    last_name,
    mock_get_company_profile,
):
    mock_get_company_profile.return_value = {
        'postal_full_name': full_name,
    }
    request = rf.get('/')
    request.user = BusinessSSOUser(session_id=123)
    mixin = PrepopulateFormMixin()
    mixin.request = request

    assert mixin.guess_given_name == first_name
    assert mixin.guess_family_name == last_name


@pytest.mark.parametrize(
    'full_name,first_name,last_name',
    (
        ('James Example', 'James', 'Example'),
        ('James', 'James', None),
        ('James Earl Jones', 'James', 'Jones'),
        ('', None, None),
    ),
)
def test_retrieve_company_profile_mixin_name_guessing_user(
    rf,
    full_name,
    first_name,
    last_name,
    company_profile,
):
    company_profile.return_value = create_response(status_code=404)
    request = rf.get('/')
    request.user = BusinessSSOUser(session_id=123, first_name=first_name, last_name=last_name)
    mixin = PrepopulateFormMixin()
    mixin.request = request

    assert mixin.guess_given_name == first_name
    assert mixin.guess_family_name == last_name
