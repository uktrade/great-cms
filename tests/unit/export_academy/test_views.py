from datetime import datetime, timedelta, timezone
from unittest import mock

import pytest
from directory_forms_api_client import actions
from django.urls import reverse

from config import settings
from core.models import HeroSnippet
from core.snippet_slugs import EXPORT_ACADEMY_LISTING_PAGE_HERO
from export_academy.filters import EventFilter
from export_academy.models import Event
from sso.models import BusinessSSOUser
from tests.unit.export_academy import factories


@pytest.fixture
def test_event_list_hero():
    snippet = HeroSnippet(slug=EXPORT_ACADEMY_LISTING_PAGE_HERO)
    snippet.save()
    return snippet


@pytest.mark.django_db
def test_export_academy_landing_page(client, export_academy_landing_page, export_academy_site):
    response = client.get(export_academy_landing_page.url)
    assert response.status_code == 200
    assert export_academy_landing_page.title in str(response.rendered_content)


@pytest.mark.django_db
def test_export_academy_event_list_page(client, export_academy_landing_page, test_event_list_hero):
    # Listing page needs a hero snippet instance to work
    url = reverse('export_academy:upcoming-events')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_export_academy_event_list_page_context(client, user, export_academy_landing_page, test_event_list_hero):
    event = factories.EventFactory()
    registration = factories.RegistrationFactory(email=user.email)
    url = reverse('export_academy:upcoming-events')

    client.force_login(user)

    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    response = client.get(url)

    assert isinstance(response.context['filter'], EventFilter)
    assert response.context['landing_page'] == export_academy_landing_page


@pytest.mark.django_db
def test_export_academy_registration_page(client, user):
    event = factories.EventFactory()
    client.force_login(user)

    url = reverse('export_academy:registration', kwargs=dict(booking_id=event.id))
    response = client.get(url)

    assert response.status_code == 200
    assert 'Please enter your details to register for Export Academy' in str(response.rendered_content)


@pytest.mark.django_db
def test_export_academy_registration_page_redirect(client):
    event = factories.EventFactory()
    url = reverse('export_academy:registration', kwargs=dict(booking_id=event.id))
    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(reverse('core:signup'))


@pytest.mark.parametrize(
    'page_url,page_content,expected_status_code',
    (
        (
            reverse('export_academy:booking-success'),
            {
                'text': 'Booking confirmation page',
            },
            200,
        ),
        (
            reverse('export_academy:registration-success'),
            {
                'text': 'We&#x27;ve received your registration form',
            },
            200,
        ),
    ),
)
@pytest.mark.django_db
def test_export_academy_success_views(client, user, page_url, page_content, expected_status_code):
    client.force_login(user)
    response = client.get(page_url)

    assert response.status_code == expected_status_code
    assert page_content['text'] in str(response.rendered_content)


@mock.patch.object(actions, 'GovNotifyEmailAction')
@pytest.mark.django_db
def test_export_academy_registration_success(mock_action_class, client, user, valid_registration_form_data):
    client.force_login(user)

    event = factories.EventFactory()
    url = reverse('export_academy:registration', kwargs=dict(booking_id=event.id))

    response = client.post(url, valid_registration_form_data)

    assert response.status_code == 302
    assert response.url == reverse('export_academy:registration-success')
    assert mock_action_class.call_count == 2
    assert mock_action_class.call_args_list[0] == mock.call(
        template_id=settings.EXPORT_ACADEMY_NOTIFY_REGISTRATION_TEMPLATE_ID,
        email_address=user.email,
        form_url=url,
    )
    assert mock_action_class.call_args_list[1] == mock.call(
        email_address=user.email,
        template_id=settings.EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID,
        form_url=url,
    )
    assert mock_action_class().save.call_count == 2


@pytest.mark.django_db
def test_export_academy_booking_redirect_to_login(client, user):
    event = factories.EventFactory()
    url = reverse('export_academy:booking')
    form_data = {'event_id': [event.id], 'status': ['Confirmed']}
    response = client.post(url, form_data)

    assert response.status_code == 302
    assert response.url.startswith(reverse('core:signup'))


@pytest.mark.django_db
def test_export_academy_booking_redirect(client, user):
    event = factories.EventFactory()
    url = reverse('export_academy:booking')
    form_data = {'event_id': [event.id], 'status': ['Confirmed']}
    client.force_login(user)
    response = client.post(url, form_data)

    assert response.status_code == 302
    assert response.url == reverse('export_academy:registration', kwargs=dict(booking_id=event.id))


@mock.patch.object(actions, 'GovNotifyEmailAction')
@pytest.mark.django_db
def test_export_academy_booking_success(mock_notify_booking, client, user):
    factories.RegistrationFactory(email=user.email)

    event = factories.EventFactory()
    url = reverse('export_academy:booking')
    form_data = {'event_id': [event.id], 'status': ['Confirmed']}

    client.force_login(user)

    assert len(factories.Booking.objects.all()) == 0

    response = client.post(url, form_data)

    assert len(factories.Booking.objects.all()) == 1
    assert factories.Booking.objects.first().status == 'Confirmed'  # type: ignore
    assert response.status_code == 302
    assert response.url == reverse('export_academy:booking-success')
    assert mock_notify_booking.call_count == 1
    assert mock_notify_booking.call_args_list == [
        mock.call(
            email_address=user.email,
            template_id=settings.EXPORT_ACADEMY_NOTIFY_BOOKING_TEMPLATE_ID,
            form_url=url,
        ),
    ]


@mock.patch.object(actions, 'GovNotifyEmailAction')
@pytest.mark.django_db
def test_export_academy_booking_cancellation_success(mock_notify_cancellation, client, user):
    event = factories.EventFactory()
    registration = factories.RegistrationFactory(email=user.email)
    booking = factories.BookingFactory(event=event, registration=registration, status='Confirmed')
    url = reverse('export_academy:booking')
    form_data = {'event_id': [event.id], 'status': ['Cancelled']}

    client.force_login(user)

    assert len(factories.Booking.objects.all()) == 1

    response = client.post(url, form_data)

    assert len(factories.Booking.objects.all()) == 1
    assert factories.Booking.objects.get(pk=booking.id).status == 'Cancelled'
    assert response.status_code == 302
    assert response.url == reverse('export_academy:booking-success')
    assert mock_notify_cancellation.call_count == 1
    assert mock_notify_cancellation.call_args_list == [
        mock.call(
            email_address=user.email,
            template_id=settings.EXPORT_ACADEMY_NOTIFY_CANCELLATION_TEMPLATE_ID,
            form_url=url,
        ),
    ]


@pytest.mark.django_db
def test_event_detail_views(client, user):
    event = factories.EventFactory()
    url = reverse('export_academy:event-details', kwargs=dict(pk=event.id))
    response = client.get(url)

    assert response.status_code == 200
    assert '/subtitles/' in str(response.rendered_content)


@pytest.mark.django_db
def test_event_list_in_person_bookable(client, user, export_academy_landing_page, test_event_list_hero):
    now = datetime.now(tz=timezone.utc)
    event = factories.EventFactory(
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3),
        completed=None,
        cut_off_days=2,
        max_capacity=2,
        format=Event.IN_PERSON,
    )
    registration = factories.RegistrationFactory(email=user.email)
    url = reverse('export_academy:upcoming-events')

    client.force_login(user)

    response = client.get(url)
    assert "Book" in response.rendered_content

    factories.BookingFactory(event=event, registration=registration, status='Confirmed')
    response = client.get(url)
    assert "Cancel" in response.rendered_content


@pytest.mark.django_db
def test_event_list_in_person_over_subscribed(client, user, export_academy_landing_page, test_event_list_hero):
    now = datetime.now(tz=timezone.utc)
    event = factories.EventFactory(
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3),
        completed=None,
        cut_off_days=2,
        max_capacity=1,
        format=Event.IN_PERSON,
    )

    book_user = BusinessSSOUser(
        id=2,
        pk=2,
        mobile_phone_number='55512345',
        email='another@example.com',
        first_name='Another',
        last_name='Cross',
        session_id='124',
    )

    book_registration = factories.RegistrationFactory(email=book_user.email)
    factories.BookingFactory(event=event, registration=book_registration, status='Confirmed')

    factories.RegistrationFactory(email=user.email)
    url = reverse('export_academy:upcoming-events')

    client.force_login(user)
    response = client.get(url)
    assert "Book" not in response.rendered_content


@pytest.mark.django_db
def test_event_list_in_person_booking_cut_off(client, user, export_academy_landing_page, test_event_list_hero):
    now = datetime.now(tz=timezone.utc)
    factories.EventFactory(
        start_date=now + timedelta(days=3),
        end_date=now + timedelta(days=3),
        completed=None,
        cut_off_days=4,
        max_capacity=2,
        format=Event.IN_PERSON,
    )

    factories.RegistrationFactory(email=user.email)
    url = reverse('export_academy:upcoming-events')

    client.force_login(user)
    response = client.get(url)
    assert "Book" not in response.rendered_content
