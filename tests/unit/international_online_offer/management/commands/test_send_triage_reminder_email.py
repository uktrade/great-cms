from datetime import datetime, timedelta
from unittest import mock

import pytest
from django.core.management import call_command

from international_online_offer.models import UserData
from tests.helpers import create_response
from tests.unit.international_online_offer.factories import (
    TriageDataFactory,
    UserDataFactory,
)


@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@pytest.mark.django_db
def test_sends_email_when_triage_incomplete_less_than_three_days_old_and_not_already_sent(mock_notify_action):
    hashed_uuid = '123'
    user_data = UserDataFactory(hashed_uuid=hashed_uuid)
    TriageDataFactory(hashed_uuid=hashed_uuid, sector='')
    mock_notify_action().save.return_value = create_response(status_code=201)
    call_command('send_triage_reminder_email')
    assert UserData.objects.get(hashed_uuid=user_data.hashed_uuid).reminder_email_sent is not None


@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@pytest.mark.django_db
def test_does_not_send_email_when_triage_complete(mock_notify_action):
    hashed_uuid = '123'
    user_data = UserDataFactory(hashed_uuid=hashed_uuid)
    TriageDataFactory(hashed_uuid=hashed_uuid)
    mock_notify_action().save.return_value = create_response(status_code=201)
    call_command('send_triage_reminder_email')
    assert UserData.objects.get(hashed_uuid=user_data.hashed_uuid).reminder_email_sent is None


@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@pytest.mark.django_db
def test_does_not_send_email_when_older_than_three_days_created(mock_notify_action):
    hashed_uuid = '123'
    five_days_ago = datetime.now() - timedelta(days=5)
    user_data = UserDataFactory(hashed_uuid=hashed_uuid, created=five_days_ago)
    TriageDataFactory(hashed_uuid=hashed_uuid)
    mock_notify_action().save.return_value = create_response(status_code=201)
    call_command('send_triage_reminder_email')
    assert UserData.objects.get(hashed_uuid=user_data.hashed_uuid).reminder_email_sent is None
