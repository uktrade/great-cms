import iso3166

from core.helpers import get_popular_export_destinations


def get_suggested_countries_for_user(request):
    if request.user.is_authenticated:
        company = request.user.company
        if company and company.expertise_industries_labels:
            sector_label = company.expertise_industries_labels[0]
            return get_suggested_countries_for_sector(sector_label)
    return []


def get_suggested_countries_for_sector(sector_label):
    destinations = get_popular_export_destinations(sector_label)
    return [
        {'value': iso3166.countries_by_name[label.upper()].alpha2, 'label': label}
        for label, _ in destinations if label.upper() in iso3166.countries_by_name
    ]
