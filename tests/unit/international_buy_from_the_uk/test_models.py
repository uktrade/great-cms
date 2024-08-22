from wagtail.test.utils import WagtailPageTests

from international.models import GreatInternationalHomePage
from international_buy_from_the_uk.models import BuyFromTheUKIndexPage


class BuyFromTheUKHomePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            BuyFromTheUKIndexPage,
            {GreatInternationalHomePage},
        )
