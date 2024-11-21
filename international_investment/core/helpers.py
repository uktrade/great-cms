from international_online_offer.core.choices import COMPANY_LOCATION_CHOICES


def get_location_display(value):
    for key, display in COMPANY_LOCATION_CHOICES:
        if key == value:
            return display
    return value


def get_investment_opportunities_search_filters(opportunities):
    sector_filters = []
    investment_type_filters = []
    region_filters = []

    # Collecting unique filter values from available opportunities
    for opportunity in opportunities:
        if opportunity.sector not in sector_filters:
            sector_filters.append(opportunity.sector)
        if opportunity.region not in region_filters:
            region_filters.append(opportunity.region)
        if opportunity.investment_type not in investment_type_filters:
            investment_type_filters.append(opportunity.investment_type)

    sector_filters.sort()
    region_filters.sort()
    investment_type_filters.sort()

    sector_choices = tuple((sector_filter, sector_filter) for sector_filter in sector_filters)
    region_choices = tuple((region_filter, region_filter) for region_filter in region_filters)

    investment_type_choices = tuple(
        (investment_type_choice, investment_type_choice) for investment_type_choice in investment_type_filters
    )

    return sector_choices, region_choices, investment_type_choices
