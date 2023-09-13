from datetime import timedelta
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from config import settings
from export_academy.models import Event
from export_academy.tasks import (
    remove_past_events_media,
    send_automated_events_notification,
)
from tests.helpers import create_response
from tests.unit.export_academy import factories


@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@pytest.mark.django_db
def test_notify_registration(mock_notify_action, user):
    mock_notify_action().save.return_value = create_response(status_code=201)
    event = factories.EventFactory(
        name='Event name',
        start_date=timezone.now() + timedelta(minutes=settings.EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES + 31),
    )
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    send_automated_events_notification()
    expected_event_url = reverse('export_academy:event-details', kwargs={'slug': event.slug})
    current_timezone = timezone.get_current_timezone()
    event_start_date = event.start_date.astimezone(current_timezone)
    event_end_date = event.end_date.astimezone(current_timezone)
    expected_start_day = event_start_date.strftime('%-d %B %Y')
    expected_event_time = f'{event_start_date.strftime("%H:%M")} - {event_end_date.strftime("%H:%M")}'
    assert mock_notify_action.call_count == 2
    assert mock_notify_action().save.call_count == 1
    assert mock_notify_action().save.call_args == mock.call(
        {
            'first_name': user.first_name,
            'event_name': event.name,
            'event_date': expected_start_day,
            'event_time': expected_event_time,
            'event_url': expected_event_url,
        }
    )


@pytest.mark.django_db
def test_remove_video(user):
    delay_days = settings.EXPORT_ACADEMY_REMOVE_EVENT_MEDIA_AFTER_DAYS + 1
    event = factories.EventFactory(
        name='Event name',
        start_date=timezone.now() - timedelta(days=delay_days),
        completed=timezone.now() + timedelta(hours=1),
    )

    remove_past_events_media()
    treated_event = Event.objects.get(id=event.id)
    assert treated_event.video_recording is None
