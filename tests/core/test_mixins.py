import pytest

from domestic.models import DomesticHomePage
from tests.domestic import factories


@pytest.mark.django_db
def test_wagtail_admin_exclusive_page_can_only_be_created_once(root_page):

    assert DomesticHomePage.can_create_at(root_page)
    factories.DomesticHomePageFactory()
    assert DomesticHomePage.can_create_at(root_page) is False


