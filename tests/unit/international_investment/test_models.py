import pytest
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


@pytest.mark.django_db
def test_investment_ops_hcsat():
    page = InvestmentOpportunityArticlePage(title='test op', article_title='test op')

    assert page.hcsat_service_name == 'investment_ops'
    assert (
        page.get_service_csat_heading(page.hcsat_service_name)
        == 'Overall, how would you rate your experience with the\n         Investment Opportunities service today?'
    )
