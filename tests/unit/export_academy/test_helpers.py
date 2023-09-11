import base64
import datetime
import hashlib
from datetime import timedelta

import pytest
from django.contrib.auth.models import AnonymousUser
from django.test import TestCase
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_str
from wagtail_factories import DocumentFactory

from config import settings
from export_academy import helpers, models
from tests.unit.export_academy import factories


@pytest.fixture
def test_future_event():
    now = timezone.now()
    return factories.EventFactory(
        start_date=now + timedelta(hours=6),
        end_date=now + timedelta(hours=7),
        completed=None,
        name='Test event name',
    )


@pytest.fixture
def test_past_event():
    now = timezone.now()
    return factories.EventFactory(
        start_date=now - timedelta(hours=6),
        end_date=now - timedelta(hours=5),
        completed=None,
        name='Test event name',
    )


@pytest.fixture
def test_registration():
    registration = models.Registration(
        first_name='test', last_name='test', email='test@example.com', external_id='123456789'
    )
    registration.save()
    return registration


@pytest.mark.django_db
def test_book_button_returned_for_upcoming_event_registered_user(user, test_future_event):
    factories.RegistrationFactory(email=user.email)
    buttons = helpers.get_buttons_for_event(user, test_future_event)

    assert buttons['form_event_booking_buttons'] == [
        {
            'label': 'Book event<span class="great-visually-hidden">Test event name</span>',
            'classname': 'govuk-button govuk-!-margin-bottom-0 ukea-ga-tracking',
            'type': 'submit',
            'value': 'Confirmed',
        }
    ]

    user = AnonymousUser()
    buttons = helpers.get_buttons_for_event(user, test_future_event)

    assert buttons['form_event_booking_buttons'] == [
        {
            'label': 'Sign up to book event<span class="great-visually-hidden"> Test event name</span>',
            'classname': 'govuk-button govuk-!-margin-bottom-0 ukea-ga-tracking',
            'value': 'Confirmed',
            'type': 'submit',
        },
    ]


@pytest.mark.django_db
def test_book_button_returned_for_upcoming_event_not_registered_user(user, test_future_event):
    buttons = helpers.get_buttons_for_event(user, test_future_event)

    assert buttons['form_event_booking_buttons'] == [
        {
            'label': 'Book event<span class="great-visually-hidden">Test event name</span>',
            'classname': 'govuk-button govuk-!-margin-bottom-0 ukea-ga-tracking',
            'value': 'Confirmed',
            'type': 'submit',
        },
    ]


@pytest.mark.django_db
def test_cancel_button_returned_for_booked_upcoming_event(user, test_future_event):
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=test_future_event, registration=registration, status='Confirmed')

    buttons = helpers.get_buttons_for_event(user, test_future_event)

    assert buttons['form_event_booking_buttons'] == [
        {
            'label': 'Cancel booking<span class="great-visually-hidden"> for Test event name</span>',
            'classname': 'govuk-button govuk-button--secondary ukea-ga-tracking govuk-!-margin-bottom-0',
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
            'classname': 'govuk-button ukea-ga-tracking govuk-!-margin-bottom-0',
            'label': """Join event<span class="great-visually-hidden">opens in new tab</span>
            <i class="fa fa-external-link-alt govuk-!-margin-right-0 govuk-!-margin-left-2" aria-hidden="true"></i>""",
            'title': 'Join Test event name',
            'url': reverse_lazy('export_academy:join', kwargs=dict(event_id=event.id)),
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
            'classname': 'govuk-button ukea-ga-tracking govuk-!-margin-bottom-0',
            'label': """Join event<span class="great-visually-hidden">opens in new tab</span>
            <i class="fa fa-external-link-alt govuk-!-margin-right-0 govuk-!-margin-left-2" aria-hidden="true"></i>""",
            'title': 'Join Test event name',
            'url': reverse_lazy('export_academy:join', kwargs=dict(event_id=event.id)),
        }
    ]


@pytest.mark.django_db
def test_view_buttons_returned_for_booked_online_past_event(user):
    now = timezone.now()
    event = factories.EventFactory(
        start_date=now - timedelta(days=2, hours=1),
        end_date=now - timedelta(days=2),
        completed=now,
        format='online',
        name='Test event name',
    )
    event.document = DocumentFactory()
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    buttons = helpers.get_buttons_for_event(user, event)

    assert buttons['event_action_buttons'] == [
        {
            'url': reverse_lazy('export_academy:event-video', kwargs=dict(pk=event.pk)),
            'label': """<i class="fa fa-play" aria-hidden="true"></i>Play
                            <span class="great-visually-hidden"> recording of Test event name</span>""",
            'classname': 'govuk-button ukea-ga-tracking govuk-!-margin-bottom-0',
            'title': 'Play recording of Test event name',
        },
    ]


@pytest.mark.django_db
def test_no_action_buttons_returned_for_booked_in_person_past_event(user):
    now = timezone.now()
    event = factories.EventFactory(
        start_date=now - timedelta(days=2, hours=1),
        end_date=now - timedelta(days=2),
        completed=now,
        format='in_person',
        name='Test event name',
    )
    event.document = DocumentFactory()
    registration = factories.RegistrationFactory(email=user.email, first_name=user.first_name)
    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    buttons = helpers.get_buttons_for_event(user, event)

    assert buttons['event_action_buttons'] == []


@pytest.mark.django_db
def test_is_export_academy_unregistered():
    user = AnonymousUser()

    assert helpers.is_export_academy_registered(user) is False


@pytest.mark.django_db
def test_is_export_academy_registered(user):
    factories.RegistrationFactory(email=user.email)

    assert helpers.is_export_academy_registered(user) is True


@pytest.mark.django_db
def test_book_button_disabled_for_closed_event(user):
    now = timezone.now()
    factories.RegistrationFactory(email=user.email)
    event = factories.EventFactory(
        start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7), completed=None, closed=True
    )

    buttons = helpers.get_buttons_for_event(user, event)

    assert buttons['form_event_booking_buttons'] == []
    assert buttons['disable_text'] == 'Closed for booking'


@pytest.mark.django_db
def test_no_join_button_when_on_confirmation(user, test_future_event):
    buttons = helpers.get_buttons_for_event(user, test_future_event, on_confirmation=True)

    assert buttons.get('event_action_buttons') == []


@pytest.mark.django_db
def test_ics_button_is_primary_on_confirmation(user, test_future_event):
    registration = factories.RegistrationFactory(email=user.email)
    factories.BookingFactory(event=test_future_event, registration=registration, status='Confirmed')
    buttons = helpers.get_buttons_for_event(user, test_future_event, on_confirmation=True)

    assert 'govuk-button--secondary' not in buttons['calendar_button']['classname']


def test_get_empty_sectors_list():
    sectors_list = []
    sectors_string = helpers.get_sectors_string(sectors_list)
    assert sectors_string == ''


def test_get_blank_sectors_list():
    sectors_list = [None, None, None]
    sectors_string = helpers.get_sectors_string(sectors_list)
    assert sectors_string == ''


def test_get_1_sectors_list():
    sectors_list = ['primary sector']
    sectors_string = helpers.get_sectors_string(sectors_list)
    assert sectors_string == 'Primary sector'


def test_get_2_sectors_list():
    sectors_list = ['primary sector', 'second sector']
    sectors_string = helpers.get_sectors_string(sectors_list)
    assert sectors_string == 'Primary sector, Second sector'


def test_get_3_sectors_list():
    sectors_list = ['primary sector', 'second sector', 'third sector']
    sectors_string = helpers.get_sectors_string(sectors_list)
    assert sectors_string == 'Primary sector, Second sector, Third sector'


@pytest.mark.django_db
def test_get_registration_from_unique_link_success(test_registration):
    idb64 = force_str(base64.b64encode(bytes(test_registration.external_id, 'utf-8')))
    token = hashlib.sha256(test_registration.email.encode('UTF-8')).hexdigest()
    assert helpers.get_registration_from_unique_link(token=token, idb64=idb64) == test_registration


@pytest.mark.parametrize(
    'external_id,email',
    (
        ('', 'test@example.com'),
        ('123456789', 'another@email.com'),
        ('987654321', 'test@example.com'),
    ),
)
@pytest.mark.django_db
def test_get_registration_from_unique_link_failure(test_registration, external_id, email):
    idb64 = force_str(base64.b64encode(bytes(external_id, 'utf-8')))
    token = hashlib.sha256(email.encode('UTF-8')).hexdigest()
    assert helpers.get_registration_from_unique_link(token=token, idb64=idb64) is None


@pytest.mark.django_db
class GetBadgesForEventTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def set_fixtures(self, test_future_event, test_past_event, user):
        self.user = user
        self.future_event = test_future_event
        self.past_event = test_past_event

    def test_user_registered_and_booked(self):
        registration = factories.RegistrationFactory(email=self.user.email)
        factories.BookingFactory(event=self.future_event, registration=registration, status='Confirmed')
        badges = helpers.get_badges_for_event(self.user, self.future_event)

        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0]['label'], 'Booked')

    def test_user_not_registered_event_ended(self):
        user = AnonymousUser()
        event = factories.EventFactory(
            end_date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),
            completed=None,
            closed=False,
        )

        badges = helpers.get_badges_for_event(user, event)

        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0]['label'], 'Ended')

    def test_user_not_registered_event_completed(self):
        user = AnonymousUser()
        event = factories.EventFactory(
            end_date=datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=1),
            completed=None,
            closed=False,
        )

        badges = helpers.get_badges_for_event(user, event)

        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0]['label'], 'Ended')

    def test_user_not_registered_event_closed(self):
        user = AnonymousUser()
        event = factories.EventFactory(
            end_date=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
            completed=None,
            closed=True,
        )

        badges = helpers.get_badges_for_event(user, event)

        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0]['label'], 'Closed')

    def test_user_registered_event_ended(self):
        registration = factories.RegistrationFactory(email=self.user.email)
        factories.BookingFactory(event=self.past_event, registration=registration, status='Confirmed')
        badges = helpers.get_badges_for_event(self.user, self.past_event)
        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0]['label'], 'Ended')

    def test_user_registered_event_completed(self):
        registration = factories.RegistrationFactory(email=self.user.email)
        factories.BookingFactory(event=self.past_event, registration=registration, status='Confirmed')
        event = factories.EventFactory()

        badges = helpers.get_badges_for_event(self.user, event)

        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0]['label'], 'Ended')

    def test_user_registered_event_closed(self):
        registration = factories.RegistrationFactory(email=self.user.email)
        factories.BookingFactory(event=self.future_event, registration=registration, status='Confirmed')
        event = self.future_event
        event.closed = True
        badges = helpers.get_badges_for_event(self.user, event)

        self.assertEqual(len(badges), 1)
        self.assertEqual(badges[0]['label'], 'Booked')
