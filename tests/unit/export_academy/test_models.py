from datetime import datetime
from unittest import mock

import pytest
from directory_forms_api_client import actions
from django.core.exceptions import ValidationError

from export_academy.models import Booking, VideoOnDemandPageTracking
from .factories import (
    BookingFactory,
    EventFactory,
    GreatMediaFactory,
    RegistrationFactory,
    VideoOnDemandPageTrackingFactory,
)


@pytest.mark.django_db
def test_event_model_to_string():
    instance = EventFactory()
    assert str(instance) == f"{instance.name} ({instance.start_date.strftime('%d-%m-%Y')})"


@pytest.mark.django_db
def test_registration_model_to_string():
    instance = RegistrationFactory()
    assert str(instance) == instance.email


@pytest.mark.parametrize('status,is_cancelled', ((Booking.CANCELLED, True), (Booking.CONFIRMED, False)))
@pytest.mark.django_db
def test_booking_is_cancelled_property(status, is_cancelled):
    booking = BookingFactory(status=status)
    assert booking.is_cancelled == is_cancelled


@mock.patch.object(actions, 'GovNotifyEmailAction')
@pytest.mark.django_db
def test_event_model_save_notification(mock_notify_cancellation, client, user):
    event = EventFactory()
    # make sure notify is not called on save
    assert mock_notify_cancellation.call_count == 0
    registration = RegistrationFactory(email=user.email)
    BookingFactory(event=event, registration=registration, status='Confirmed')

    # set the default value
    event._loaded_values = dict(completed=None)
    # Update completed
    event.completed = datetime.now()
    event.save()
    # Now that event is completed, notify should be called
    assert mock_notify_cancellation.call_count == 1


@pytest.mark.django_db
def test_video_on_demand_page_tracking_model_user_already_recorded(user):
    event = EventFactory()
    already_tracked = VideoOnDemandPageTracking.user_already_recorded(user.email, event, event.video_recording)
    assert already_tracked is False

    VideoOnDemandPageTrackingFactory(user_email=user.email, event=event, video=event.video_recording)
    already_tracked = VideoOnDemandPageTracking.user_already_recorded(user.email, event, event.video_recording)
    assert already_tracked is True


@pytest.mark.django_db
def test_videoondemandpagetracking_model_to_string():
    event = EventFactory()
    video = GreatMediaFactory()
    instance = VideoOnDemandPageTracking(user_email='Joe.Bloggs@gmail.com', event=event, video=video)
    assert str(instance) == f'User: Joe.Bloggs@gmail.com, Event: {event.id}, Video: {video.id}'


@mock.patch.object(actions, 'GovNotifyEmailAction')
@pytest.mark.django_db
def test_event_model_save_fails_when_completed_but_not_closed(mock_notify_cancellation, client, user):
    event = EventFactory()

    # Ensure event is completed, and open for bookings
    event.completed = datetime.now()
    event.closed = False
    event._loaded_values = {'complete': None}

    # Ensure saving event raises a validation Error
    with pytest.raises(ValidationError) as excinfo:
        event.save()
    assert str(excinfo.value) == "Event must be marked 'Closed for Bookings' before it can be marked 'Completed'"
