from datetime import datetime, timedelta
from unittest import mock

import pytest
from directory_forms_api_client import actions
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone

from config import settings
from core.models import HeroSnippet
from core.snippet_slugs import (
    EA_REGISTRATION_PAGE_HERO,
    EXPORT_ACADEMY_LISTING_PAGE_HERO,
)
from export_academy.filters import EventFilter
from export_academy.models import Booking
from tests.unit.export_academy import factories


@pytest.fixture
def test_event_list_hero():
    snippet = HeroSnippet(slug=EXPORT_ACADEMY_LISTING_PAGE_HERO)
    snippet.save()
    return snippet


@pytest.fixture
def test_registration_hero():
    snippet = HeroSnippet(slug=EA_REGISTRATION_PAGE_HERO)
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
def test_export_academy_registration_page(
    client,
    user,
    test_registration_hero,
    export_academy_landing_page,
):
    event = factories.EventFactory()
    client.force_login(user)

    url = reverse('export_academy:registration', kwargs=dict(event_id=event.id))
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_export_academy_registration_page_redirect(client):
    event = factories.EventFactory()
    url = reverse('export_academy:registration', kwargs=dict(event_id=event.id))
    response = client.get(url)

    assert response.status_code == 302
    assert response.url.startswith(reverse('core:signup'))


@mock.patch.object(actions, 'GovNotifyEmailAction')
# @mock.patch('export_academy.views.SuccessPageView.user_just_registered')
@pytest.mark.django_db
def test_registration_success_view(
    mock_user_just_registered,
    valid_registration_form_data,
    client,
    user,
    export_academy_landing_page,
    test_registration_hero,
):
    client.force_login(user)
    event = factories.EventFactory()
    registration = factories.RegistrationFactory(email=user.email)
    factories.BookingFactory(event=event, registration=registration)
    url = reverse('export_academy:registration-confirm')

    client.post(
        reverse('export_academy:registration', kwargs={'event_id': event.id}),
        valid_registration_form_data,
    )

    response = client.post(
        url,
        {
            'completed': datetime.now(),
        },
        follow=True,
    )

    assert response.status_code == 200
    assert response.context['just_registered']
    assert 'Registration confirmed' in response.rendered_content


@pytest.mark.parametrize(
    'booking_status,success_url,text',
    (
        (Booking.CONFIRMED, 'export_academy:booking-success', 'Booking confirmed'),
        (Booking.CANCELLED, 'export_academy:cancellation-success', 'Cancellation confirmed'),
    ),
)
@pytest.mark.django_db
def test_booking_success_view(
    export_academy_landing_page, test_event_list_hero, client, user, booking_status, success_url, text
):
    client.force_login(user)
    registration = factories.RegistrationFactory(email=user.email)
    event = factories.EventFactory()
    booking = factories.BookingFactory(event=event, status=booking_status, registration=registration)

    response = client.get(reverse('export_academy:booking-success', kwargs={'booking_id': booking.id}))

    assert response.status_code == 200
    assert text in response.rendered_content


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url,error_messages',
    (
        (
            reverse('export_academy:registration-details'),
            {
                'first_name': 'Test name',
                'last_name': 'Test last',
                'job_title': 'Astronaut',
                'phone_number': '072345678910',
            },
            reverse('export_academy:registration-experience'),
            {
                'first_name': 'Enter your name',
                'last_name': 'Enter your family name',
                'job_title': 'Enter your job title',
                'phone_number': 'Please enter a valid UK phone number',
            },
        ),
        (
            reverse('export_academy:registration-experience'),
            {
                'export_experience': 'I do not have a product for export',
                'sector': 'Agriculture, horticulture, fisheries and pets',
                'export_product': 'Goods',
            },
            reverse('export_academy:registration-business'),
            {
                'export_experience': 'Please answer this question',
                'sector': 'Please answer this question',
                'export_product': 'Please answer this question',
            },
        ),
        (
            reverse('export_academy:registration-business'),
            {
                'business_name': 'Test Business',
                'business_postcode': 'SW1A 1AA',
                'annual_turnover': 'Up to £85,000',
                'employee_count': '10 to 49',
            },
            reverse('export_academy:registration-marketing'),
            {
                'business_name': 'Enter your business name',
                'business_postcode': 'Enter your business postcode',
                'annual_turnover': 'Please answer this question',
                'employee_count': 'Please answer this question',
            },
        ),
        (
            reverse('export_academy:registration-marketing'),
            {
                'marketing_sources': 'Other',
            },
            reverse('export_academy:registration-confirm'),
            {
                'marketing_sources': 'Please answer this question',
            },
        ),
    ),
)
@pytest.mark.django_db
def test_export_academy_registration_form_pages(
    page_url,
    form_data,
    redirect_url,
    error_messages,
    client,
    user,
    test_registration_hero,
    export_academy_landing_page,
):
    client.force_login(user)

    #   Redirect fails when any of the fields in the form are missing
    invalid_form_data = form_data.copy()
    for key in form_data:
        invalid_form_data.pop(key)
        response = client.post(page_url, invalid_form_data)
        assert response.status_code == 200
        assert error_messages[key] in str(response.rendered_content)
        invalid_form_data = form_data.copy()

    #   Redirect succeeds with valid data
    response = client.post(page_url, form_data)
    assert response.status_code == 302
    assert response.url == redirect_url

    #   When editing registration details the redirect returns to the confirm page
    page_url += 'edit/'
    assert client.get(page_url).context['button_text'] == 'Save'
    response = client.post(page_url, form_data)
    assert response.status_code == 302
    assert response.url == reverse('export_academy:registration-confirm')


@mock.patch.object(actions, 'GovNotifyEmailAction')
@pytest.mark.django_db
def test_export_academy_registration_success(
    mock_action_class,
    client,
    user,
    valid_registration_form_data,
    test_registration_hero,
    export_academy_landing_page,
):
    client.force_login(user)

    event = factories.EventFactory()
    registration = factories.RegistrationFactory(email=user.email)
    booking = factories.BookingFactory(event=event, registration=registration, status=Booking.CANCELLED)
    url = reverse('export_academy:registration-confirm')

    client.post(
        reverse('export_academy:registration', kwargs={'event_id': event.id}),
        valid_registration_form_data,
    )

    assert client.session['event_id'] == event.id

    response = client.post(
        url,
        {
            'completed': datetime.now(),
        },
    )

    assert response.status_code == 302
    assert response.url == reverse('export_academy:registration-success', kwargs={'booking_id': booking.id})

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
    assert response.url == reverse('export_academy:registration', kwargs=dict(event_id=event.id))


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
    booking = factories.Booking.objects.first()

    assert booking.status == 'Confirmed'  # type: ignore
    assert response.status_code == 302
    # here
    assert response.url == reverse('export_academy:booking-success', kwargs={'booking_id': booking.id})

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
    assert response.url == reverse('export_academy:cancellation-success', kwargs={'booking_id': booking.id})
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
    event = factories.EventFactory(name='Test event name', description='Test description')
    url = reverse('export_academy:event-details', kwargs=dict(pk=event.id))
    response = client.get(url)

    assert response.status_code == 200
    assert '/subtitles/' in str(response.rendered_content)
    assert '<a href="/export-academy/events/?booking_period=past" class="govuk-link">Back</a>' in str(
        response.rendered_content
    )
    assert 'time' in str(response.rendered_content)
    assert 'Duration:' in str(response.rendered_content)
    assert 'Test event name' in str(response.rendered_content)
    assert 'Test description' in str(response.rendered_content)


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
