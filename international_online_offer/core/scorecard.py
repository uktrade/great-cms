from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import hirings, regions, sectors as sectors, spends


def score_is_high_value(sector, location, hiring, spend, spend_other=0):
    is_high_value_capex = False
    is_high_value_labour_workforce_hire = False
    is_high_value_hpo = False

    if sector:
        if spend:
            is_high_value_capex = is_capex_spend(sector, spend, spend_other)
        if hiring:
            is_high_value_labour_workforce_hire = is_labour_workforce_hire(sector, hiring)
        if location:
            is_high_value_hpo = is_hpo(sector, location)

    return is_high_value_capex or is_high_value_labour_workforce_hire or is_high_value_hpo


def get_upper_value(value_in):
    return value_in.split('-')[1]


def is_capex_spend(sector, spend, spend_other=0):
    capex_sector_spend = [
        {sectors.TECHNOLOGY_AND_SMART_CITIES: 2400000},
        {directory_constants_sectors.CONSUMER_AND_RETAIL: 848513},
        {sectors.PHARMACEUTICALS_AND_BIOTECHNOLOGY: 2099999},
        {directory_constants_sectors.ENERGY: 499999},
    ]
    if spend == spends.SPECIFIC_AMOUNT:
        spend_upper_value = spend_other
    elif '+' in spend:
        spend_upper_value = spend.split('+')[0]
    else:
        spend_upper_value = get_upper_value(spend)

    spend_upper_value = int(spend_upper_value)

    for sector_spend in capex_sector_spend:
        if sector in sector_spend:
            if spend_upper_value >= sector_spend[sector]:
                return True
    return False


def is_labour_workforce_hire(sector, hiring):
    labour_workforce_hire_sector_hiring = [
        {directory_constants_sectors.FOOD_AND_DRINK: 12},
        {sectors.TECHNOLOGY_AND_SMART_CITIES: 11},
        {directory_constants_sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES: 11},
        {directory_constants_sectors.CONSUMER_AND_RETAIL: 15},
        {sectors.CREATIVE_INDUSTRIES: 9},
        {sectors.HEALHCARE_SERVICES: 10},
        {sectors.MEDICAL_DEVICES_AND_EQUIPMENT: 10},
    ]

    if hiring == hirings.NO_PLANS_TO_HIRE_YET:
        hiring_upper_value = 0
    elif '+' in hiring:
        hiring_upper_value = hiring.split('+')[0]
    else:
        hiring_upper_value = get_upper_value(hiring)

    hiring_upper_value = int(hiring_upper_value)

    for sector_hiring in labour_workforce_hire_sector_hiring:
        if sector in sector_hiring:
            if hiring_upper_value >= sector_hiring[sector]:
                return True
    return False


def is_hpo(sector, location):
    hpo_sector_location = [
        {directory_constants_sectors.FOOD_AND_DRINK: [regions.NORTH_EAST, regions.NORTH_WEST, regions.EAST_OF_ENGLAND]},
        {
            sectors.TECHNOLOGY_AND_SMART_CITIES: [
                regions.WALES,
                regions.SOUTH_WEST,
                regions.EAST_OF_ENGLAND,
                regions.WEST_MIDLANDS,
                regions.YORKSHIRE_AND_THE_HUMBER,
            ]
        },
        {
            sectors.CREATIVE_INDUSTRIES: [
                regions.NORTH_EAST,
                regions.WEST_MIDLANDS,
                regions.SOUTH_EAST,
            ]
        },
        {
            directory_constants_sectors.ENERGY: [
                regions.NORTH_EAST,
                regions.SCOTLAND,
                regions.SOUTH_EAST,
            ]
        },
        {
            sectors.PHARMACEUTICALS_AND_BIOTECHNOLOGY: [
                regions.NORTH_EAST,
                regions.SCOTLAND,
                regions.YORKSHIRE_AND_THE_HUMBER,
                regions.EAST_MIDLANDS,
                regions.NORTH_WEST,
                regions.EAST_OF_ENGLAND,
                regions.WALES,
                regions.NORTHERN_IRELAND,
            ]
        },
    ]

    for sector_location in hpo_sector_location:
        if sector in sector_location:
            if location in sector_location[sector]:
                return True
    return False
