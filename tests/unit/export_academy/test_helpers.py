from datetime import datetime, timedelta

import pytest
from django.contrib.auth.models import AnonymousUser

from export_academy.helpers import EventButtonHelper, is_export_academy_registered
from tests.unit.export_academy import factories


@pytest.mark.django_db
def book_button_shown_for_upcoming_event(user):
    now = datetime.now()
    factories.RegistrationFactory(email=user.email)
    event = factories.EventFactory(start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7))

    buttons = EventButtonHelper().get_buttons_for_obj(user, event)

    assert buttons['form_event_booking_buttons'] is [
        {
            'label': 'Book',
            'classname': 'link',
            'value': 'Confirmed',
            'type': 'submit',
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
