import pytest
from wagtail.tests.utils import WagtailPageTests

from international_online_offer.models import IOOGuidePage, IOOLandingPage


class IOOLandingPageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOLandingPage,
            {
                IOOLandingPage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            IOOLandingPage,
            {
                IOOLandingPage,
                IOOGuidePage,
            },
        )


class IOOGuidePageTests(WagtailPageTests):
    def test_allowed_parents(self):
        self.assertAllowedParentPageTypes(
            IOOGuidePage,
            {
                IOOLandingPage,
            },
        )

    def test_allowed_children(self):
        self.assertAllowedSubpageTypes(
            IOOGuidePage,
            {},
        )


@pytest.mark.django_db
def test_ioo_guide_page_content(rf):
    guide_page = IOOGuidePage(title='Guide')
    request = rf.get(guide_page.url)
    context = guide_page.get_context(request)
    assert context['complete_contact_form_message'] == IOOGuidePage.LOW_VALUE_INVESTOR_CONTACT_FORM_MESSAGE
    assert context['complete_contact_form_link'] == 'international_online_offer:contact'
    assert context['complete_contact_form_link_text'] == 'Complete form'
    assert context['contact_form_success_message'] == IOOGuidePage.CONTACT_FORM_SUCCESS_MESSAGE
    assert context['complete_contact_form_link'] == 'international_online_offer:contact'
