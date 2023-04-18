def score_is_high_value(sector, location, hiring, spend, spend_other=0):
    is_high_value_levelling_up = False
    is_high_value_capex = False
    is_high_value_labour_workforce_hire = False
    is_high_value_hpo = False
    if location:
        is_high_value_levelling_up = is_levelling_up(location)

    if sector:
        if spend:
            is_high_value_capex = is_capex_spend(sector, spend, spend_other)
        if hiring:
            is_high_value_labour_workforce_hire = is_labour_workforce_hire(sector, hiring)
        if location:
            is_high_value_hpo = is_hpo(sector, location)

    return is_high_value_levelling_up or is_high_value_capex or is_high_value_labour_workforce_hire or is_high_value_hpo


def is_levelling_up(location):
    REGIONS = [
        'East Midlands',
        'East of England',
        'North East',
        'North West',
        'Northern Ireland',
        'Scotland',
        'South West',
        'Wales',
        'West Midlands',
        'Yorkshire and The Humber',
    ]
    return location in REGIONS


def get_upper_value(value_in):
    return value_in.split('-')[1]


def is_capex_spend(sector, spend, spend_other=0):
    SECTOR_SPEND_LIST = [
        {'Food and Drink': 2000000},
        {'Technology and Smart Cities': 2400000},
        {'Financial and Professional Services': 6000000},
        {'Consumer and retail': 5000000},
        {'Creative industries': 5000000},
    ]
    if spend == 'Specific amount':
        spend_upper_value = spend_other
    elif '+' in spend:
        spend_upper_value = spend.split('+')[0]
    else:
        spend_upper_value = get_upper_value(spend)

    spend_upper_value = int(spend_upper_value)

    for sector_spend in SECTOR_SPEND_LIST:
        if sector in sector_spend:
            if spend_upper_value >= sector_spend[sector]:
                return True
    return False


def is_labour_workforce_hire(sector, hiring):
    SECTOR_HIRING_LIST = [
        {'Food and Drink': 12},
        {'Technology and Smart Cities': 15},
        {'Financial and Professional Services': 11},
        {'Consumer and retail': 15},
        {'Creative industries': 15},
    ]

    if hiring == 'No plans to hire yet':
        hiring_upper_value = 0
    elif '+' in hiring:
        hiring_upper_value = hiring.split('+')[0]
    else:
        hiring_upper_value = get_upper_value(hiring)

    hiring_upper_value = int(hiring_upper_value)

    for sector_hiring in SECTOR_HIRING_LIST:
        if sector in sector_hiring:
            if hiring_upper_value >= sector_hiring[sector]:
                return True
    return False


def is_hpo(sector, location):
    SECTOR_LOCATION_LIST = [
        {'Food and Drink': ['North East', 'North West', 'East']},
        {'Technology and Smart Cities': ['Wales', 'South West', 'East', 'West Midlands', 'Yorkshire and the Humber']},
    ]

    for sector_location in SECTOR_LOCATION_LIST:
        if sector in sector_location:
            if location in sector_location[sector]:
                return True
    return False
