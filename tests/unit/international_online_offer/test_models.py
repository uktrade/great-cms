from wagtail.tests.utils import WagtailPageTests

from international_online_offer.models import IOOGuidePage, IOOLandingPage


class IOOLandingPageTests(WagtailPageTests):
    def test_ioo_landing_page_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOLandingPage,
            {
                IOOLandingPage,
            },
        )

    def test_ioo_landing_page_allowed_children(self):
        self.assertAllowedSubpageTypes(
            IOOLandingPage,
            {
                IOOLandingPage,
                IOOGuidePage,
            },
        )


class IOOGuidePageTests(WagtailPageTests):
    def test_ioo_guide_page_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOGuidePage,
            {
                IOOLandingPage,
            },
        )

    def test_ioo_guide_page_allowed_children(self):
        self.assertAllowedSubpageTypes(
            IOOGuidePage,
            {},
        )
