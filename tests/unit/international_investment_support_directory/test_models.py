from wagtail.test.utils import WagtailPageTests

from international.models import GreatInternationalHomePage
from international_investment_support_directory.models import (
    InvestmentSupportDirectoryIndexPage,
)


class InvestmentSupportDirectoryHomePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            InvestmentSupportDirectoryIndexPage,
            {GreatInternationalHomePage},
        )
