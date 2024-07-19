from international_investment.core.choices import (
    SPEND_CHOICES,
    SPEND_CHOICES_EURO,
    SPEND_CHOICES_USD,
)
from international_online_offer.core.choices import COMPANY_LOCATION_CHOICES


def get_location_display(value):
    for key, display in COMPANY_LOCATION_CHOICES:
        if key == value:
            return display
    return value


def get_spend_choices_by_currency(currency):
    spend_choices = SPEND_CHOICES
    if currency == 'EUR':
        spend_choices = SPEND_CHOICES_EURO
    elif currency == 'USD':
        spend_choices = SPEND_CHOICES_USD
    return spend_choices
