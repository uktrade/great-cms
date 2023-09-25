from django import template
from django.conf import settings

from core.cms_slugs import DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE

register = template.Library()


@register.simple_tag()
def get_contact_breadcrumb_details():
    if settings.FEATURE_DIGITAL_POINT_OF_ENTRY:
        return {'url': DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE, 'text': 'Guidance and Support'}
    else:
        return {'url': 'contact:contact-us-routing-form', 'text': 'Contact us'}
