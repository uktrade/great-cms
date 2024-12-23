from config.celery import app
from international_online_offer.core import scorecard
from international_online_offer.models import TriageData
from international_online_offer.services import (
    get_all_sectors_gva_scoring_criteria,
    get_dbt_sectors,
)


@app.task
def rescore_eyb_users():
    """
    Function that will be called periodically to update EYB users high/low value investor scoring
    based on most recent Gross Value Add bandings from Data Workspace
    """
    gva_scoring_criteria = get_all_sectors_gva_scoring_criteria()
    dbt_sectors = get_dbt_sectors()

    for user_triage_data in TriageData.objects.all():
        if user_triage_data.sector_id:
            sector_row = next(
                (sector for sector in dbt_sectors if sector['sector_id'] == user_triage_data.sector_id), None
            )
            full_sector_name = sector_row['full_sector_name']

            is_high_value = scorecard.score_is_high_value(
                full_sector_name,
                user_triage_data.location,
                user_triage_data.hiring,
                user_triage_data.spend,
                user_triage_data.hashed_uuid,
                scorecard_criteria=gva_scoring_criteria[full_sector_name],
            )

            if is_high_value != user_triage_data.is_high_value:
                user_triage_data.is_high_value = is_high_value
                user_triage_data.save()
