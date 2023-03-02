from datetime import datetime, timedelta
from unittest import mock

import pytest

from config import settings
from export_academy.tasks import send_automated_notification
from tests.helpers import create_response
from tests.unit.export_academy import factories


@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@pytest.mark.django_db
def test_notify_registration(mock_notify_action, user):
    mock_notify_action().save.return_value = create_response(status_code=201)
    event = factories.EventFactory(
        name='Event name',
        start_date=datetime.now() + timedelta(minutes=settings.EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES + 1),
    )
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    send_automated_notification()

    assert mock_notify_action.call_count == 2
    assert mock_notify_action().save.call_count == 1
    assert mock_notify_action().save.call_args == mock.call(
        {'first_name': user.first_name, 'event_names': 'Event name'}
    )
