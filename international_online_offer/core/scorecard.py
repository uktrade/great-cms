from international_online_offer.core import hirings
from international_online_offer.models import ScorecardCriterion

scorecard_criteria = ScorecardCriterion.objects.all()


# Scoring system takes input from EYB triage and calculates whether a user / investor is low or high value.
# ISD use this to contact high value users for help setting up in the UK
# The numbers are given to us from ISD and tranferred into this scoring system.
def score_is_high_value(sector, location, hiring, spend):
    # Requirement from stakeholders was that we only score based on three metrics:
    # How much they are looking to spend.
    # How many people they'll be creating jobs for.
    # Choice of location (Regional level)

    is_high_value_capex = False
    is_high_value_labour_workforce_hire = False
    is_high_value_hpo = False

    if sector:
        if spend:
            is_high_value_capex = is_capex_spend(sector, spend)
        if hiring:
            is_high_value_labour_workforce_hire = is_labour_workforce_hire(sector, hiring)
        if location:
            is_high_value_hpo = is_hpo(sector, location)

    # If the user gets a positive for any of these metrics they are considered high value
    return is_high_value_capex or is_high_value_labour_workforce_hire or is_high_value_hpo


def get_upper_value(value_in):
    return value_in.split('-')[1]


def get_capex_scoring_table():
    return [{criterion.sector: criterion.capex_spend} for criterion in scorecard_criteria if criterion.capex_spend]


def get_labour_workforce_hiring_scoring_table():
    return [
        {criterion.sector: criterion.labour_workforce_hire}
        for criterion in scorecard_criteria
        if criterion.labour_workforce_hire
    ]


def get_hpo_scoring_table():
    return [
        {criterion.sector: criterion.high_potential_opportunity_locations}
        for criterion in scorecard_criteria
        if criterion.high_potential_opportunity_locations
    ]


def is_capex_spend(sector, spend):
    # Scoring criteria includes sector and the value
    if '+' in spend:
        spend_upper_value = spend.split('+')[0]
    else:
        spend_upper_value = get_upper_value(spend)

    spend_upper_value = int(spend_upper_value)

    for sector_spend in get_capex_scoring_table():
        if sector in sector_spend and spend_upper_value >= sector_spend[sector]:
            return True

    return False


def is_labour_workforce_hire(sector, hiring):
    if hiring == hirings.NO_PLANS_TO_HIRE_YET:
        hiring_upper_value = 0
    elif '+' in hiring:
        hiring_upper_value = hiring.split('+')[0]
    else:
        hiring_upper_value = get_upper_value(hiring)

    hiring_upper_value = int(hiring_upper_value)

    for sector_hiring in get_labour_workforce_hiring_scoring_table():
        if sector in sector_hiring and hiring_upper_value >= sector_hiring[sector]:
            return True

    return False


def is_hpo(sector, location):
    for sector_location in get_hpo_scoring_table():
        if sector in sector_location:
            if location in sector_location[sector]:
                return True
    return False
