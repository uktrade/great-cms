import pytest
from wagtail.core.models import Page
from wagtail_factories import SiteFactory, PageFactory

from tests.domestic import factories


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
