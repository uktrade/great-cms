from django import template

from international_online_offer.core import choices
from international_online_offer.services import get_country_display_name

register = template.Library()


@register.filter
def get_location_display(value):
    for v, d in choices.REGION_CHOICES:
        if v == value:
            return d

    return value


@register.filter
def get_company_location_display(company_location: str) -> str:
    return get_country_display_name(company_location)
