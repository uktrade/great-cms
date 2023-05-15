from datetime import timedelta
from unittest import mock

import pytest
from directory_forms_api_client import actions
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from config import settings
from core.models import HeroSnippet
from core.snippet_slugs import EXPORT_ACADEMY_LISTING_PAGE_HERO
from export_academy.filters import EventFilter
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
# Listing page needs a hero snippet instance to work
def test_export_academy_event_list_page_logged_out(client, export_academy_landing_page, test_event_list_hero):
    now = timezone.now()
    factories.EventFactory.create_batch(
        5, start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7), completed=None
    )
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
def test_download_ics(client, user):
    event = factories.EventFactory()
    url = reverse('export_academy:calendar')
    form_data = {'event_id': [event.id]}

    response = client.post(url, form_data)

    assert response.status_code == 200
    content = response.content.decode()
    assert event.name in content


# Remove 2 following tests after UKEA release 2.
@pytest.mark.django_db
def test_release_2_views(client, user, export_academy_landing_page, test_event_list_hero):
    event = factories.EventFactory(name='Test event name')
    registration = factories.RegistrationFactory(email=user.email)
    url = reverse('export_academy:upcoming-events')

    client.force_login(user)

    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    response = client.get(url)

    assert 'title="Play recording of Test event name"' in response.rendered_content


@pytest.mark.django_db
@override_settings(FEATURE_EXPORT_ACADEMY_RELEASE_2=False)
def test_release_1_views(client, user, export_academy_landing_page, test_event_list_hero):
    event = factories.EventFactory()
    registration = factories.RegistrationFactory(email=user.email)
    url = reverse('export_academy:upcoming-events')

    client.force_login(user)

    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    response = client.get(url)

    assert 'www.events.great.gov.uk' in response.rendered_content
