from unittest import mock

import pytest
from django.urls import reverse

<<<<<<< HEAD
<<<<<<< HEAD
from tests.unit.export_academy import factories

=======
>>>>>>> 95019f7a6 (Refactor views to handle bookings and registrations + tidy up)
=======
from tests.unit.export_academy import factories

>>>>>>> 76017e8d9 (Test forms & helpers)

@pytest.mark.django_db
def test_export_academy_landing_page(client, export_academy_landing_page, export_academy_site):
    response = client.get(export_academy_landing_page.url)

    assert response.status_code == 200
    assert export_academy_landing_page.title in str(response.rendered_content)


@pytest.mark.django_db
def test_export_academy_event_list_page(client):
    url = reverse('export_academy:upcoming-events')
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 76017e8d9 (Test forms & helpers)
def test_export_academy_event_list_page_context(client, user):
    event = factories.EventFactory()
    registration = factories.RegistrationFactory(email=user.email)
    url = reverse('export_academy:upcoming-events')

    client.force_login(user)

    response = client.get(url)

    assert list(response.context['bookings']) == []

    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    response = client.get(url)

    assert list(response.context['bookings']) == [event.id]


@pytest.mark.django_db
<<<<<<< HEAD
=======
>>>>>>> 95019f7a6 (Refactor views to handle bookings and registrations + tidy up)
=======
>>>>>>> 76017e8d9 (Test forms & helpers)
def test_export_academy_registration_page(client, user):
    client.force_login(user)

    url = reverse('export_academy:registration')
    response = client.get(url)

    assert response.status_code == 200
    assert 'Please enter your details to register for Export Academy' in str(response.rendered_content)


@pytest.mark.django_db
def test_export_academy_registration_page_redirect(client):
    url = reverse('export_academy:registration')
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


@mock.patch('export_academy.helpers.notify_registration')
@pytest.mark.django_db
<<<<<<< HEAD
<<<<<<< HEAD
def test_export_academy_registration_success(mock_notify_registration, client, user, valid_registration_form_data):
    client.force_login(user)

    url = reverse('export_academy:registration')

    response = client.post(url, valid_registration_form_data)
=======
def test_export_academy_registration_success(mock_notify_registration, client, user):
=======
def test_export_academy_registration_success(mock_notify_registration, client, user, valid_registration_form_data):
>>>>>>> 76017e8d9 (Test forms & helpers)
    client.force_login(user)

    url = reverse('export_academy:registration')

<<<<<<< HEAD
    response = client.post(url, form_data)
>>>>>>> 95019f7a6 (Refactor views to handle bookings and registrations + tidy up)
=======
    response = client.post(url, valid_registration_form_data)
>>>>>>> 76017e8d9 (Test forms & helpers)

    assert response.status_code == 302
    assert response.url == reverse('export_academy:registration-success')
    assert mock_notify_registration.call_count == 1
    assert mock_notify_registration.call_args_list == [
        mock.call(
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 76017e8d9 (Test forms & helpers)
            email_data={
                'business_name': valid_registration_form_data['business_name'],
                'first_name': valid_registration_form_data['first_name'],
            },
<<<<<<< HEAD
=======
            email_data={'business_name': form_data['business_name'], 'first_name': form_data['first_name']},
>>>>>>> 95019f7a6 (Refactor views to handle bookings and registrations + tidy up)
=======
>>>>>>> 76017e8d9 (Test forms & helpers)
            form_url=url,
            email_address=user.email,
        ),
    ]
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 76017e8d9 (Test forms & helpers)


@pytest.mark.django_db
def test_export_academy_booking_redirect(client):
    event = factories.EventFactory()
    url = reverse('export_academy:booking')
    form_data = {'event_id': [event.id], 'status': ['Confirmed']}

    response = client.post(url, form_data)

    assert response.status_code == 302
    assert response.url == reverse('export_academy:registration')


@pytest.mark.django_db
def test_export_academy_booking_success(client, user):
    factories.RegistrationFactory(email=user.email)

    event = factories.EventFactory()
    url = reverse('export_academy:booking')
    form_data = {'event_id': [event.id], 'status': ['Confirmed']}

    client.force_login(user)

    assert len(factories.Booking.objects.all()) == 0

    response = client.post(url, form_data)

    assert len(factories.Booking.objects.all()) == 1
    assert factories.Booking.objects.first().status == 'Confirmed'
    assert response.status_code == 302
    assert response.url == reverse('export_academy:booking-success')


@pytest.mark.django_db
def test_export_academy_booking_cancellation_success(client, user):
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
<<<<<<< HEAD
=======
>>>>>>> 95019f7a6 (Refactor views to handle bookings and registrations + tidy up)
=======
>>>>>>> 76017e8d9 (Test forms & helpers)
