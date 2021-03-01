from unittest import mock

import pytest

from core.mixins import GetSnippetContentMixin
from domestic.models import DomesticHomePage
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

    mock_snippet_instance = mock.Mock(name='mock_snippet_instance')

    mock_snippet_model = mock.Mock(name='mock_snippet_model')
    mock_snippet_model.objects.get.return_value = mock_snippet_instance

    mock_module = mock.Mock(name='mock_module')
    mock_module.FakeTestSnippet = mock_snippet_model

    with mock.patch('core.mixins.import_module') as mock_import_module:
        mock_import_module.return_value = mock_module
        assert test_view.get_snippet_instance() == mock_snippet_instance

    mock_snippet_model.objects.get.assert_called_once_with(slug='foo-bar-baz')
