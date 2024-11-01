from wagtail.test.utils import WagtailPageTests

from international.models import GreatInternationalHomePage
from international_investment.models import (
    InvestmentArticlePage,
    InvestmentIndexPage,
    InvestmentOpportunityArticlePage,
    InvestmentRegionsPage,
    InvestmentSectorsPage,
)


class InvestmentHomePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            InvestmentIndexPage,
            {GreatInternationalHomePage},
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            InvestmentIndexPage,
            {InvestmentSectorsPage, InvestmentRegionsPage, InvestmentOpportunityArticlePage, InvestmentArticlePage},
        )


class InvestmentSectorsPageTests(WagtailPageTests):

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(InvestmentSectorsPage, {InvestmentArticlePage})


class InvestmentRegionsPageTests(WagtailPageTests):

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(InvestmentRegionsPage, {InvestmentArticlePage})
