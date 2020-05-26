from wagtail.tests.utils import WagtailPageTests
from core import mixins
from domestic.models import DomesticHomePage


class DomesticHomePageTests(WagtailPageTests):

    def test_page_is_exclusive(self):
        assert issubclass(DomesticHomePage, mixins.WagtailAdminExclusivePageMixin)
