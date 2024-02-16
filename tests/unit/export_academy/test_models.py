from datetime import datetime

import pytest
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


@pytest.mark.django_db
def test_event_model_save_fails_when_completed_but_not_closed():
    event = EventFactory()

    # Ensure event is completed, and open for bookings
    event.completed = datetime.now()
    event.closed = False
    event._loaded_values = {'completed': None}

    # Ensure saving event raises a validation Error
    with pytest.raises(ValidationError) as excinfo:
        event.clean()
    assert excinfo.value == ValidationError(
        "Event must be marked 'Closed for Bookings' before it can be marked 'Completed'"
    )
