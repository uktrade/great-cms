from datetime import timedelta

import pytest
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse_lazy
from django.utils import timezone
from wagtail_factories import DocumentFactory

from config import settings
from export_academy import helpers
from tests.unit.export_academy import factories


@pytest.mark.django_db
def test_book_button_returned_for_upcoming_event_registered_user(user):
    now = timezone.now()
    factories.RegistrationFactory(email=user.email)
    event = factories.EventFactory(
        start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7), completed=None, name='Test event name'
    )

    buttons = helpers.get_buttons_for_event(user, event)

    assert buttons['form_event_booking_buttons'] == [
        {
            'label': 'Book<span class="great-visually-hidden"> Test event name</span>',
            'classname': 'govuk-button govuk-!-margin-bottom-0',
            'value': 'Confirmed',
            'type': 'submit',
        },
    ]


@pytest.mark.django_db
def test_book_button_returned_for_upcoming_event_not_registered_user(user):
    now = timezone.now()
    event = factories.EventFactory(
        start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7), completed=None, name='Test event name'
    )

    buttons = helpers.get_buttons_for_event(user, event)

    assert buttons['form_event_booking_buttons'] == [
        {
            'label': 'Book<span class="great-visually-hidden"> Test event name</span>',
            'classname': 'govuk-button govuk-!-margin-bottom-0',
            'value': 'Confirmed',
            'type': 'submit',
        },
    ]


@pytest.mark.django_db
def test_cancel_button_returned_for_booked_upcoming_event(user):
    now = timezone.now()
    event = factories.EventFactory(
        start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7), completed=None, name='Test event name'
    )
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    buttons = helpers.get_buttons_for_event(user, event)

    assert buttons['form_event_booking_buttons'] == [
        {
            'label': 'Cancel booking<span class="great-visually-hidden"> for Test event name</span>',
            'classname': 'govuk-button govuk-button--secondary',
            'value': 'Cancelled',
            'type': 'submit',
        },
    ]


@pytest.mark.django_db
def test_join_button_returned_for_booked_in_progress_event(user):
    now = timezone.now()
    event = factories.EventFactory(
        start_date=now - timedelta(minutes=settings.EXPORT_ACADEMY_EVENT_ALLOW_JOIN_BEFORE_START_MINS),  # type: ignore
        end_date=now + timedelta(hours=1),
        completed=None,
        name='Test event name',
    )
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    buttons = helpers.get_buttons_for_event(user, event)

    assert buttons['event_action_buttons'] == [
        {
            'url': event.link,
            'label': 'Join<span class="great-visually-hidden"> Test event name</span>',
            'classname': 'govuk-button govuk-button--secondary',
            'title': 'Join Test event name',
        }
    ]


@pytest.mark.django_db
def test_join_button_returned_for_booked_in_upcoming_event(user):
    now = timezone.now()
    event = factories.EventFactory(
        start_date=now + timedelta(days=1),
        end_date=now + timedelta(days=1, hours=1),
        completed=None,
        name='Test event name',
    )
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    buttons = helpers.get_buttons_for_event(user, event)

    assert buttons['event_action_buttons'] == [
        {
            'url': event.link,
            'label': 'Join<span class="great-visually-hidden"> Test event name</span>',
            'classname': 'govuk-button govuk-button--secondary',
            'title': 'Join Test event name',
        }
    ]


@pytest.mark.django_db
def test_view_buttons_returned_for_booked_past_event(user):
    now = timezone.now()
    event = factories.EventFactory(
        start_date=now - timedelta(days=2, hours=1),
        end_date=now - timedelta(days=2),
        completed=now,
        name='Test event name',
    )
    event.document = DocumentFactory()
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    buttons = helpers.get_buttons_for_event(user, event)

    assert buttons['event_action_buttons'] == [
        {
            'url': reverse_lazy('export_academy:event-details', kwargs=dict(pk=event.pk)),
            'label': """<i class="fa fa-play" aria-hidden="true"></i>Play
                             <span class="great-visually-hidden"> recording of Test event name</span>""",
            'classname': 'govuk-button',
            'title': 'Play recording of Test event name',
        },
        {
            'url': event.document.url,
            'label': """<i class="fa fa-download" aria-hidden="true"></i>
                             Download PDF<span class="great-visually-hidden"> for Test event name</span>""",
            'classname': 'govuk-button govuk-button--secondary',
            'title': 'Download PDF for Test event name',
        },
    ]


@pytest.mark.django_db
def test_is_export_academy_unregistered():
    user = AnonymousUser()

    assert helpers.is_export_academy_registered(user) is False


@pytest.mark.django_db
def test_is_export_academy_registered(user):
    factories.RegistrationFactory(email=user.email)

    assert helpers.is_export_academy_registered(user) is True


@pytest.mark.django_db
def test_param_builder_sets_navigation_defaults(user, rf, client):
    factories.RegistrationFactory(email=user.email)
    request = rf.get('/')
    request.user = user
    request.session = client.session

    assert helpers.build_request_navigation_params(request).dict() == {'navigation': 'all'}
    assert 'navigation' not in request.session


@pytest.mark.django_db
def test_param_builder_persists_navigation_choice_in_session(user, rf, client):
    factories.RegistrationFactory(email=user.email)
    request = rf.get('/', {'navigation': 'booked'})
    request.user = user
    request.session = client.session

    assert helpers.build_request_navigation_params(request).dict() == {'navigation': 'booked'}
    assert 'navigation' in request.session
    assert request.session['navigation'] == 'booked'
