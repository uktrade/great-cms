from django.core.management import call_command

from config.celery import app
from international_online_offer.core import scorecard
from international_online_offer.models import TriageData
from international_online_offer.services import (
    get_all_sectors_gva_scoring_criteria,
    get_dbt_sectors,
)


from datetime import timedelta
from django.utils import timezone


@app.task
def rescore_eyb_users():
    """
    Function that will be called periodically to update EYB users high/low value investor scoring
    based on most recent Gross Value Add bandings from Data Workspace, but only for records modified
    within the last 6 months.
    """
    # Get the date 6 months ago
    six_months_ago = timezone.now() - timedelta(days=6 * 30)  # Approximation of 6 months

    gva_scoring_criteria = get_all_sectors_gva_scoring_criteria()
    dbt_sectors = get_dbt_sectors()

    # Filter TriageData objects to only those modified within the last 6 months
    recent_triage_data = TriageData.objects.filter(modified__gte=six_months_ago)

    for user_triage_data in recent_triage_data:
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


@app.task
def check_trade_association_links():
    call_command('check_trade_association_links')
