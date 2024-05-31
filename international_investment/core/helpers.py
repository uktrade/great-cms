from international_online_offer.core.choices import COMPANY_LOCATION_CHOICES


def get_location_display(value):
    for key, display in COMPANY_LOCATION_CHOICES:
        if key == value:
            return display
    return value
