from wagtail.test.utils import WagtailPageTests

from domestic.models import GreatDomesticHomePage
from international.models import GreatInternationalHomePage


class GreatInternationalHomePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            GreatInternationalHomePage,
            {GreatDomesticHomePage},
        )
