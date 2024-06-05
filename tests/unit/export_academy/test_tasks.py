from datetime import timedelta
from unittest import mock

import pytest
from django.urls import reverse
from django.utils import timezone

from config import settings
from export_academy.models import Event
from export_academy.tasks import (
    remove_past_events_media,
    send_automated_event_complete_notification,
    send_automated_events_notification,
)
from tests.helpers import create_response
from tests.unit.export_academy import factories


@mock.patch('directory_forms_api_client.actions.GovNotifyBulkEmailAction')
@pytest.mark.django_db
def test_notify_registration_valid_event(mock_notify_action, user):
    """
    Test notification to attendees who have booked an upcoming Event. Notification is sent to directory-forms-api
    for email processing.
    """

    mock_notify_action().save.return_value = create_response(status_code=201)

    # Create a valid Event + associated Booking
    event_valid = factories.EventFactory(
        name='Event name',
        start_date=timezone.now() + timedelta(minutes=settings.EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES + 31),
    )
    registration_valid = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event_valid, registration=registration_valid, status='Confirmed')

    # Run task - we are looking for a single email being sent
    send_automated_events_notification()

    # Build expected call arguments
    expected_event_url = reverse('export_academy:event-details', kwargs={'slug': event_valid.slug})
    current_timezone = timezone.get_current_timezone()
    event_start_date = event_valid.start_date.astimezone(current_timezone)
    event_end_date = event_valid.end_date.astimezone(current_timezone)
    expected_start_day = event_start_date.strftime('%-d %B %Y')
    expected_event_time = f'{event_start_date.strftime("%H:%M")} - {event_end_date.strftime("%H:%M")}'

    # Verify call arguments match expected
    assert mock_notify_action.call_count == 2
    assert mock_notify_action().save.call_count == 1
    assert mock_notify_action().save.call_args == mock.call(
        {
            'template_id': 'b446f2be-8c92-40af-a5c8-e21b8d9e8077',
            'bulk_email_entries': [
                {
                    'first_name': 'Jim',
                    'event_name': 'Event name',
                    'email_address': 'jim@example.com',
                    'event_date': expected_start_day,
                    'event_time': expected_event_time,
                    'event_url': expected_event_url,
                }
            ],
        }
    )


@mock.patch('directory_forms_api_client.actions.GovNotifyBulkEmailAction')
@pytest.mark.django_db
def test_notify_registration_invalid_event_outside_time_range(mock_notify_action, user):
    """
    Test Event notification to attendees who have booked an upcoming Event that is outside the time filter
    range. No notification should be sent.
    """

    mock_notify_action().save.return_value = create_response(status_code=201)

    # Create a valid Event + associated Booking
    event_valid = factories.EventFactory(
        name='Event name',
        start_date=timezone.now() + timedelta(minutes=settings.EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES + 61),
    )
    registration_valid = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event_valid, registration=registration_valid, status='Confirmed')

    # Run task - we are looking for a NO notifications being sent
    send_automated_events_notification()

    # Verify call arguments match expected
    assert mock_notify_action.call_count == 1
    assert mock_notify_action().save.call_count == 0


@mock.patch('directory_forms_api_client.actions.GovNotifyBulkEmailAction')
@pytest.mark.django_db
def test_notify_registration_invalid_event_booking_cancelled(mock_notify_action, user):
    """
    Test Event notification to attendees who have booked an upcoming Event, but then cancelled.
    No notification should be sent.
    """

    mock_notify_action().save.return_value = create_response(status_code=201)

    # Create a valid Event + associated Booking
    event_valid = factories.EventFactory(
        name='Event name',
        start_date=timezone.now() + timedelta(minutes=settings.EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES + 61),
    )
    registration_valid = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event_valid, registration=registration_valid, status='Cancelled')

    # Run task - we are looking for a NO notifications being sent
    send_automated_events_notification()

    # Verify call arguments match expected
    assert mock_notify_action.call_count == 1
    assert mock_notify_action().save.call_count == 0


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


@mock.patch('directory_forms_api_client.actions.GovNotifyBulkEmailAction')
@pytest.mark.django_db
def test_notify_event_complete_valid_event(mock_complete_action, user):
    """
    We want to create an Event that has marked as completed with the last 15 minutes, and ensure a notification that
    the event is complete is sent to directory-forms-api, to then be sent as an email to the end user.
    """

    mock_complete_action().save.return_value = create_response(status_code=201)

    # Create event with one booking
    event = factories.EventFactory(name='Event name', completed=timezone.now(), completed_email_sent=False)
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    # Run task - we are looking for a single email being sent
    assert mock_complete_action.call_count == 1
    send_automated_event_complete_notification()
    assert mock_complete_action.call_count == 2
    assert mock_complete_action().save.call_count == 1
    assert mock_complete_action().save.call_args == mock.call(
        {
            'template_id': 'ff45b258-ae9e-4939-a049-089d959ddfee',
            'bulk_email_entries': [
                {'first_name': user.first_name, 'event_name': event.name, 'email_address': user.email}
            ],
        }
    )

    # Verify booking has been updated in DB as 'email sent'
    event = Event.objects.filter(id=event.id).first()
    assert event.completed_email_sent is True


@mock.patch('directory_forms_api_client.actions.GovNotifyBulkEmailAction')
@pytest.mark.django_db
def test_notify_event_complete_cancelled_email_not_sent(mock_complete_action, user):
    """
    We want to create an event that has marked as completed with the last 15 minutes, with an associated booking that
    has been cancelled, and ensure an email notification is not sent.
    """

    mock_complete_action().save.return_value = create_response(status_code=201)

    # Create event with one booking
    event = factories.EventFactory(name='Event name', completed=timezone.now(), completed_email_sent=False)
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Cancelled')

    # Run task - we are looking for no notifications being sent
    assert mock_complete_action.call_count == 1
    send_automated_event_complete_notification()
    assert mock_complete_action.call_count == 2
    assert mock_complete_action().save.call_count == 1
    assert mock_complete_action().save.call_args == mock.call(
        {'template_id': 'ff45b258-ae9e-4939-a049-089d959ddfee', 'bulk_email_entries': []}
    )

    # Verify Event has been updated in DB as email sent.
    event = Event.objects.filter(id=event.id).first()
    assert event.completed_email_sent is True


@mock.patch('directory_forms_api_client.actions.GovNotifyBulkEmailAction')
@pytest.mark.django_db
def test_notify_event_previously_complete_email_not_sent(mock_complete_action, user):
    """
    We want to create an event that has marked as completed_email_sent, and ensure an email notification
    is NOT sent.
    """

    mock_complete_action().save.return_value = create_response(status_code=201)

    # Create event with one booking
    event = factories.EventFactory(
        name='Event name', completed=timezone.now() - timedelta(days=30), completed_email_sent=True
    )
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    # Run task - we are looking for no emails being sent
    assert mock_complete_action.call_count == 1
    send_automated_event_complete_notification()
    assert mock_complete_action.call_count == 1
    assert mock_complete_action().save.call_count == 0
    assert mock_complete_action().save.call_args is None

    # Verify Event is still showing as 'completed email sent'
    event = Event.objects.filter(id=event.id).first()
    assert event.completed_email_sent is True


@mock.patch('directory_forms_api_client.actions.GovNotifyBulkEmailAction')
@pytest.mark.django_db
def test_notify_event_unpublished_email_not_sent(mock_complete_action, user):
    """
    We want to create an event that is unpublished, and ensure an email notification
    is NOT sent.
    """

    mock_complete_action().save.return_value = create_response(status_code=201)

    # Create event with one booking
    event = factories.EventFactory(
        name='Event name',
        start_date=timezone.now() + timedelta(minutes=settings.EXPORT_ACADEMY_AUTOMATED_NOTIFY_TIME_DELAY_MINUTES + 31),
    )
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    event.live = None
    event.save()

    # Run task - we are looking for no emails being sent
    assert mock_complete_action.call_count == 1
    send_automated_event_complete_notification()
    assert mock_complete_action.call_count == 1
    assert mock_complete_action().save.call_count == 0
    assert mock_complete_action().save.call_args is None
