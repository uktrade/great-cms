from datetime import datetime, timedelta, timezone

import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse_lazy
from wagtail_factories import DocumentFactory

from config import settings
from export_academy.helpers import get_buttons_for_event, is_export_academy_registered
from tests.unit.export_academy import factories


@pytest.mark.django_db
def test_book_button_returned_for_upcoming_event(user):
    now = datetime.now(tz=timezone.utc)
    factories.RegistrationFactory(email=user.email)
    event = factories.EventFactory(start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7))

    buttons = get_buttons_for_event(user, event)

    assert buttons['form_event_booking_buttons'] == [
        {
            'label': 'Book',
            'classname': 'link',
            'value': 'Confirmed',
            'type': 'submit',
        },
    ]


@pytest.mark.django_db
def test_cancel_button_returned_for_booked_upcoming_event(user):
    now = datetime.now(tz=timezone.utc)
    event = factories.EventFactory(start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7))
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    buttons = get_buttons_for_event(user, event)

    assert buttons['form_event_booking_buttons'] == [
        {
            'label': 'Cancel',
            'classname': 'link',
            'value': 'Cancelled',
            'type': 'submit',
        },
    ]


@pytest.mark.django_db
def test_join_button_returned_for_booked_in_progress_event(user):
    now = datetime.now(tz=timezone.utc)
    event = factories.EventFactory(
        start_date=now - timedelta(minutes=settings.EXPORT_ACADEMY_EVENT_ALLOW_JOIN_BEFORE_START_MINS),
        end_date=now + timedelta(hours=1),
    )
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    buttons = get_buttons_for_event(user, event)

    assert buttons['event_action_buttons'] == [
        {'url': event.link, 'label': 'Join', 'classname': 'text', 'title': 'Join'}
    ]


@pytest.mark.django_db
def test_view_buttons_returned_for_booked_past_event(user):
    now = datetime.now(tz=timezone.utc)
    event = factories.EventFactory(
        start_date=now - timedelta(days=2, hours=1), end_date=now - timedelta(days=2), completed=True
    )
    event.document = DocumentFactory()
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    buttons = get_buttons_for_event(user, event)

    assert buttons['event_action_buttons'] == [
        {
            'url': reverse_lazy('export_academy:event-details', kwargs=dict(pk=event.pk)),
            'label': 'View video',
            'classname': 'text',
            'title': 'View video',
        },
        {
            'url': event.document.url,
            'label': 'View slideshow',
            'classname': 'text',
            'title': 'View slideshow',
        },
    ]


@pytest.mark.django_db
def test_is_export_academy_unregistered():
    user = AnonymousUser()

    assert is_export_academy_registered(user) is False


@pytest.mark.django_db
def test_is_export_academy_registered(user):
    factories.RegistrationFactory(email=user.email)

    assert is_export_academy_registered(user) is True
