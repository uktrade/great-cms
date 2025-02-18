from django.db.models import Q
from sentry_sdk import capture_message

from international_investment.models import InvestmentOpportunityArticlePage
from international_online_offer.core import hirings, spends
from international_online_offer.services import get_gva_scoring_criteria


# Scoring system takes input from EYB triage and calculates whether a user / investor is low or high value.
# ISD use this to contact high value users for help setting up in the UK
# The numbers are given to us from ISD and tranferred into this scoring system.
def score_is_high_value(sector, location, hiring, spend, user_uuid, scorecard_criteria=None):
    # Requirement from stakeholders was that we only score based on three metrics:
    # How much they are looking to spend.
    # How many people they'll be creating jobs for.
    # Choice of location (Regional level)

    # if scorecard criteria has not been passed retrieve from API
    if not scorecard_criteria:
        scorecard_criteria = get_gva_scoring_criteria(full_sector_name=sector)
        if len(scorecard_criteria) == 1:
            scorecard_criteria = scorecard_criteria[0]
        else:
            # edge case where no scoring available for a user's sector (e.g. misalignment between dbt sector list
            # and gva bandings). The user doesn't need to be notified but the issue should be investigated as there
            # may be false negatives
            capture_message(f'Scoring failed for user ID {user_uuid}.')
            return False

    is_high_value_capex = False
    is_high_value_labour_workforce_hire = False
    is_high_value_hpo = False

    # using band c as requested by stakeholders
    band_threshold = scorecard_criteria['value_band_c_minimum']

    if scorecard_criteria['sector_classification_value_band'] == 'Capital intensive':
        is_high_value_capex = is_capex_spend(spend, band_threshold)
    elif scorecard_criteria['sector_classification_value_band'] == 'Labour intensive':
        is_high_value_labour_workforce_hire = is_labour_workforce_hire(hiring, band_threshold)

    is_high_value_hpo = is_hpo(sector, location)

    # If the user gets a positive for any of these metrics they are considered high value
    return is_high_value_capex or is_high_value_labour_workforce_hire or is_high_value_hpo


def get_value(value_in: str) -> int:
    if '+' in value_in:
        return int(value_in.split('+')[0])
    elif '-' in value_in:
        return int(value_in.split('-')[1])
    return 0


def is_capex_spend(spend, threshold):
    # the maximum value a user can choose is £5m+ so we return true to accommodate sectors with a gva banding >£5m
    if spend == spends.MORE_THAN_FIVE_MILLION:
        return True
    else:
        spend_upper_value = get_value(spend)
        return spend_upper_value >= threshold


def is_labour_workforce_hire(hiring, threshold):
    # the maximum value a user can choose is 21+ so we return true to accommodate sectors with a gva banding 21
    if hiring == hirings.TWENTY_ONE_PLUS:
        return True

    if hiring == hirings.NO_PLANS_TO_HIRE_YET:
        hiring_upper_value = 0
    else:
        hiring_upper_value = get_value(hiring)

    return hiring_upper_value >= threshold


def is_hpo(sector, location):
    investment_opps = InvestmentOpportunityArticlePage.objects.filter(
        Q(dbt_sectors__contains=[sector]) & Q(dbt_locations__contains=[location])
    )

    if investment_opps:
        return True

    return False
