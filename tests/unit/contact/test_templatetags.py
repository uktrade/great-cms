from contact.templatetags.dep_tags import get_contact_breadcrumb_details
from core.cms_slugs import DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE


def test_get_contact_breadcrumb_details_dep_on():
    assert get_contact_breadcrumb_details() == {
        'url': DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE,
        'text': 'Guidance and Support',
    }


def test_get_contact_breadcrumb_details_dep_off():
    assert get_contact_breadcrumb_details() == {'url': 'contact:contact-us-routing-form', 'text': 'Contact us'}
