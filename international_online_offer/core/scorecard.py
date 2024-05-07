from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import hirings, regions, sectors as sectors


# Scoring system takes input from EYB triage and calculates whether a user / investor is low or high value.
# ISD use this to contact high value users for help setting up in the UK
# The numbers are given to us from ISD and tranferred into this scoring system.
def score_is_high_value(sector, dbt_sub_sector, location, hiring, spend):
    # Requirement from stakeholders was that we only score based on three metrics:
    # How much they are looking to spend.
    # How many people they'll be creating jobs for.
    # Choice of location (Regional level)

    is_high_value_capex = False
    is_high_value_labour_workforce_hire = False
    is_high_value_hpo = False

    if sector:
        if spend:
            is_high_value_capex = is_capex_spend(sector, dbt_sub_sector, spend)
        if hiring:
            is_high_value_labour_workforce_hire = is_labour_workforce_hire(sector, dbt_sub_sector, hiring)
        if location:
            is_high_value_hpo = is_hpo(sector, location)

    # If the user gets a positive for any of these metrics they are considered high value
    return is_high_value_capex or is_high_value_labour_workforce_hire or is_high_value_hpo


def get_upper_value(value_in):
    return value_in.split('-')[1]


def is_capex_spend(sector, sub_sector, spend):
    # Scoring criteria includes sector and the value
    capex_sector_spend = [
        {sectors.PHARMACEUTICALS_AND_BIOTECHNOLOGY: 3191999},
        {directory_constants_sectors.ENERGY: 3099999},
        {sectors.ADVANCED_ENGINEERING: 1031499},
        {directory_constants_sectors.AEROSPACE: 2499999},
        {directory_constants_sectors.AUTOMOTIVE: 1459999},
        {directory_constants_sectors.CHEMICALS: 1587999},
        {sectors.MARITIME: 848512},
        {directory_constants_sectors.MINING: 4425999},
        {directory_constants_sectors.RAILWAYS: 1999999},
        {sectors.SPACE: 1479999},
        {directory_constants_sectors.WATER: 3099999},
        {sectors.CREATIVE_INDUSTRIES: 505999},
        {directory_constants_sectors.AIRPORTS: 11999999},
        {sectors.MARITIME: 9999999},
        # Introduction of sub sectors added here for scoring.
        # We do not have enumns / consts for these as there are many.
        # (DBT Sub sectors in data workspace)
        {'Energy : Civil nuclear': 759999},
        {'Energy : Oil and gas': 2219999},
        {'Consumer and retail : Books, printed media and stationery': 1799999},
        {'Consumer and retail : Clothing, footwear and fashion': 499999},
        {'Technology and smart cities : Communications': 1079999},
        {'Technology and smart cities : Hardware': 2399999},
        {'Technology and smart cities : Software': 503999},
    ]
    if '+' in spend:
        spend_upper_value = spend.split('+')[0]
    else:
        spend_upper_value = get_upper_value(spend)

    spend_upper_value = int(spend_upper_value)

    for sector_spend in capex_sector_spend:
        # Sub sector scoring should override parents so we check first
        if sub_sector in sector_spend and spend_upper_value >= sector_spend[sub_sector]:
            return True
        if sector in sector_spend and spend_upper_value >= sector_spend[sector]:
            return True

    return False


def is_labour_workforce_hire(sector, sub_sector, hiring):
    labour_workforce_hire_sector_hiring = [
        {directory_constants_sectors.FOOD_AND_DRINK: 20},
        {directory_constants_sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES: 13},
        {directory_constants_sectors.CONSUMER_AND_RETAIL: 10},
        {sectors.HEALTHCARE_SERVICES: 15},
        {sectors.MEDICAL_DEVICES_AND_EQUIPMENT: 10},
        {directory_constants_sectors.CONSTRUCTION: 12},
        {sectors.DEFENCE: 19},
        {sectors.SECURITY: 19},
        {directory_constants_sectors.EDUCATION_AND_TRAINING: 11},
        {sectors.AGRICULTURE_HORTICULTURE_FISHERIES_AND_PETS: 8},
        {sectors.MARITIME: 13},
        {sectors.SPACE: 14},
        {'Financial and professional services : Business and consumer services': 14},
        {'Maritime : Maritime services': 14},
    ]

    if hiring == hirings.NO_PLANS_TO_HIRE_YET:
        hiring_upper_value = 0
    elif '+' in hiring:
        hiring_upper_value = hiring.split('+')[0]
    else:
        hiring_upper_value = get_upper_value(hiring)

    hiring_upper_value = int(hiring_upper_value)

    for sector_hiring in labour_workforce_hire_sector_hiring:
        if sub_sector in sector_hiring and hiring_upper_value >= sector_hiring[sub_sector]:
            return True
        if sector in sector_hiring and hiring_upper_value >= sector_hiring[sector]:
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
        {
            sectors.HEALTHCARE_SERVICES: [
                regions.NORTH_EAST,
                regions.SOUTH_EAST,
                regions.YORKSHIRE_AND_THE_HUMBER,
                regions.WEST_MIDLANDS,
            ]
        },
    ]

    for sector_location in hpo_sector_location:
        if sector in sector_location:
            if location in sector_location[sector]:
                return True
    return False
