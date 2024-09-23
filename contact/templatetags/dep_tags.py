from django import template

from core.cms_slugs import DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE

register = template.Library()


@register.simple_tag()
def get_contact_breadcrumb_details():
    return {'url': DIGITAL_ENTRY_POINT_TRIAGE_HOMEPAGE, 'text': 'Guidance and Support'}
