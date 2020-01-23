from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from domestic.models import DomesticHomePage


class DomesticHomePageTests(WagtailPageTests):

    def test_domestic_homepage_can_be_created_under_root(self):
        self.assertAllowedParentPageTypes(DomesticHomePage, {Page})

    def test_domestic_homepage_hero_streamfield(self):
        assert DomesticHomePage.hero.field.name == 'hero'
