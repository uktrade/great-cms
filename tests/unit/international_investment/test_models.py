from wagtail.test.utils import WagtailPageTests

from international.models import GreatInternationalHomePage
from international_investment.models import InvestmentIndexPage


class InvestmentHomePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            InvestmentIndexPage,
            {GreatInternationalHomePage},
        )
