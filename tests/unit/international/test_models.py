from wagtail.test.utils import WagtailPageTests

from domestic.models import GreatDomesticHomePage
from domestic_growth.models import DomesticGrowthHomePage
from international.models import GreatInternationalHomePage


class GreatInternationalHomePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            GreatInternationalHomePage,
            {GreatDomesticHomePage, DomesticGrowthHomePage},
        )
