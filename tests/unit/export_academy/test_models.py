from datetime import datetime
from unittest import mock

import pytest
from directory_forms_api_client import actions

from export_academy.models import Booking
from .factories import BookingFactory, EventFactory, RegistrationFactory


@pytest.mark.parametrize(
    'factory,attrs',
    ((EventFactory, ['id', 'name']), (RegistrationFactory, ['email'])),
)
@pytest.mark.django_db
def test_model_to_string(factory, attrs):
    instance = factory()
    assert str(instance) == ':'.join([str(getattr(instance, attr)) for attr in attrs])


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
