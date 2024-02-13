from datetime import datetime, timezone

import pytest
from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import override_settings

from tests.unit.core.factories import MicrositeFactory


@override_settings(MODERATION_EMAIL_DIST_LIST="davidu@mail.com")
@pytest.mark.django_db
def test_send_campaign_site_review_reminders(user, domestic_homepage):
    now = datetime.now(timezone.utc)
    first_published_at = now - relativedelta(months=12)
    User = get_user_model()

    user = User.objects.create(email='davidu@mail.com')
    MicrositeFactory(
        title='Microsite',
        first_published_at=first_published_at,
        owner=user,
        parent=domestic_homepage,
    )

    call_command('send_campaign_site_review_reminder')
