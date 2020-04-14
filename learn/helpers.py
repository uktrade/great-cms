import iso3166

from core.helpers import get_popular_export_destinations


def get_suggested_countries(sector_label):
    destinations = get_popular_export_destinations(sector_label)
    return [
        {'value': iso3166.countries_by_name[label.upper()].alpha2, 'label': label}
        for label, _ in destinations if label.upper() in iso3166.countries_by_name
    ]
