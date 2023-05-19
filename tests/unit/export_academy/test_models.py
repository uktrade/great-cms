import pytest

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
