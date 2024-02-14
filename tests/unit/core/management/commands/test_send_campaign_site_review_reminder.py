from datetime import datetime, timezone
from unittest import mock

import pytest
from dateutil.relativedelta import relativedelta
from directory_forms_api_client import actions
from django.contrib.auth import get_user_model
from django.core.management import call_command

from tests.unit.core.factories import MicrositeFactory

User = get_user_model()


@mock.patch.object(actions, 'GovNotifyEmailAction')
@pytest.mark.django_db
def test_send_campaign_site_review_reminder_with_first_published_at(
    mock_action_class, user, domestic_homepage, settings
):
    now = datetime.now(timezone.utc)
    first_published_at = now - relativedelta(months=12)

    user = User.objects.create(email='joe.bloggs@gmail.com')
    MicrositeFactory.create(
        title='Microsite',
        first_published_at=first_published_at,
        owner=user,
        parent=domestic_homepage,
    )

    settings.MODERATION_EMAIL_DIST_LIST = 'moderators@gov.uk'
    call_command('send_campaign_site_review_reminder')

    assert mock_action_class.call_count == 2

    assert mock_action_class.call_args_list == [
        mock.call(
            email_address=user.email,
            template_id=settings.CAMPAIGN_SITE_REVIEW_REMINDER_TEMPLATE_ID,
            email_reply_to_id=settings.CAMPAIGN_MODERATION_REPLY_TO_ID,
            form_url=str(),
        ),
        mock.call(
            email_address=settings.MODERATION_EMAIL_DIST_LIST,
            template_id=settings.CAMPAIGN_SITE_REVIEW_REMINDER_TEMPLATE_ID,
            email_reply_to_id=settings.CAMPAIGN_MODERATION_REPLY_TO_ID,
            form_url=str(),
        ),
    ]


@mock.patch.object(actions, 'GovNotifyEmailAction')
@pytest.mark.django_db
def test_send_campaign_site_review_reminder_with_review_reminder_sent(
    mock_action_class, user, domestic_homepage, settings
):
    now = datetime.now(timezone.utc)
    review_reminder_sent = now - relativedelta(months=12)
    first_published_at = now - relativedelta(days=1)

    user = User.objects.create(email='joe.bloggs@gmail.com')
    MicrositeFactory.create(
        title='Microsite',
        first_published_at=first_published_at,
        review_reminder_sent=review_reminder_sent,
        owner=user,
        parent=domestic_homepage,
    )

    settings.MODERATION_EMAIL_DIST_LIST = 'moderators@gov.uk'
    call_command('send_campaign_site_review_reminder')

    assert mock_action_class.call_count == 2
    assert mock_action_class.call_args_list == [
        mock.call(
            email_address=settings.MODERATION_EMAIL_DIST_LIST,
            template_id=settings.CAMPAIGN_SITE_REVIEW_REMINDER_TEMPLATE_ID,
            email_reply_to_id=settings.CAMPAIGN_MODERATION_REPLY_TO_ID,
            form_url=str(),
        ),
        mock.call(
            email_address=user.email,
            template_id=settings.CAMPAIGN_SITE_REVIEW_REMINDER_TEMPLATE_ID,
            email_reply_to_id=settings.CAMPAIGN_MODERATION_REPLY_TO_ID,
            form_url=str(),
        ),
    ]
