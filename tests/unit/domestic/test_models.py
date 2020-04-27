from wagtail.core.models import Page
from wagtail.tests.utils import WagtailPageTests
from core import mixins
from domestic.models import DomesticHomePage


class DomesticHomePageTests(WagtailPageTests):

    def test_can_be_created_under_root(self):
        self.assertAllowedParentPageTypes(DomesticHomePage, {Page})

    def test_page_is_exclusive(self):
        assert issubclass(DomesticHomePage, mixins.WagtailAdminExclusivePageMixin)
