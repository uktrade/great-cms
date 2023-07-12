from django import template

from international_online_offer.core import choices

register = template.Library()


@register.filter
def get_location_display(value):
    for v, d in choices.REGION_CHOICES:
        if v == value:
            return d

    return value
