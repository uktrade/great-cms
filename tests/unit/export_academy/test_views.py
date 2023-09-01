import base64
import hashlib
import json
from datetime import datetime, timedelta
from unittest import mock

import pytest
import wagtail_factories
from directory_forms_api_client import actions
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from config import settings
from core.models import HeroSnippet
from core.snippet_slugs import EA_REGISTRATION_PAGE_HERO
from directory_sso_api_client import sso_api_client
from export_academy.filters import EventFilter
from export_academy.models import Booking, Registration
from sso import helpers as sso_helpers
from tests.helpers import create_response
from tests.unit.export_academy import factories


@pytest.fixture
def test_registration_hero():
    snippet = HeroSnippet(slug=EA_REGISTRATION_PAGE_HERO)
    snippet.save()
    return snippet


@pytest.fixture
def test_uuid():
    return 'edb85922-2aea-4e0e-9df7-c74e5cf5ec78'


@pytest.fixture
def test_unique_link_query_params():
    registration = Registration(first_name='test', last_name='test', email='test@example.com', external_id='123456789')
    registration.save()
    idb64 = base64.b64encode(bytes(registration.external_id, 'utf-8'))
    token = hashlib.sha256(registration.email.encode('UTF-8')).hexdigest()
    return f'?idb64={idb64.decode("utf-8")}&token={token}'


@pytest.fixture
def signup_post_request_unique_link(client, test_unique_link_query_params):
    form_data = {'email': 'test@example.com', 'password': 'newPassword'}

    def post_request():
        return client.post(reverse('export_academy:signup') + test_unique_link_query_params, data=form_data)

    return post_request


@pytest.fixture
def signup_form_post_request_new_user(client):
    form_data = {'email': 'test@example.com', 'password': 'newPassword'}

    def post_request():
        return client.post(reverse('export_academy:signup'), data=form_data)

    return post_request


@pytest.fixture
def uidb64():
    return 'MjE1ODk1'


@pytest.fixture
def token():
    return 'bq1ftj-e82fb7b694d200b144012bfac0c866b2'


@pytest.fixture
def signin_form_post_request(client):
    registration = factories.RegistrationFactory(email='test@example.com')
    form_data = {'email': 'test@example.com', 'password': 'mypassword'}

    def post_request():
        return client.post(reverse('export_academy:signin') + f'?registration-id={registration.id}', data=form_data)

    return post_request


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


@pytest.mark.parametrize('page_query, num_events_on_page', (('', 10), ('?page=1', 10), ('?page=2', 5)))
@pytest.mark.django_db
def test_export_academy_event_list_pagination(
    client, page_query, num_events_on_page, export_academy_landing_page, test_event_list_hero
):
    now = timezone.now()
    factories.EventFactory.create_batch(
        15, start_date=now + timedelta(hours=6), end_date=now + timedelta(hours=7), completed=None
    )
    url = f"{reverse('export_academy:upcoming-events')}{page_query}"
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['page_obj']) == num_events_on_page


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
        {'completed': datetime.now()},
        follow=True,
    )

    assert response.status_code == 200
    assert response.context['just_registered']
    assert 'Registration confirmed' in response.rendered_content

    response = client.post(
        url,
        {'completed': datetime.now()},
        follow=True,
    )

    assert response.status_code == 200
    assert response.context['editing_registration']
    assert 'Registration update confirmed' in response.rendered_content


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
    # creates bookings for the same event to ensure correct booking is fetched
    factories.BookingFactory.create_batch(3, event=event)
    url = reverse('export_academy:registration-confirm')

    client.post(
        reverse('export_academy:registration', kwargs={'event_id': event.id}),
        valid_registration_form_data,
    )

    assert client.session['event_id'] == event.id

    response = client.post(
        url,
        {'completed': datetime.now()},
    )

    booking = Booking.objects.get(event_id=event.id, registration__email=user.email)

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

    response = client.post(
        url,
        {'completed': datetime.now()},
    )

    assert response.status_code == 302
    assert response.url == reverse('export_academy:registration-edit-success')


@pytest.mark.django_db
def test_export_academy_booking_redirect_to_login(client, user):
    event = factories.EventFactory()
    url = reverse('export_academy:booking')
    form_data = {'event_id': [event.id], 'status': ['Confirmed']}
    response = client.post(url, form_data)

    assert response.status_code == 302
    assert response.url.startswith(reverse('export_academy:signup'))


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
def test_event_video_view_with_video(client, user):
    event = factories.EventFactory(name='Test event name', description='Test description')
    url = reverse('export_academy:event-video', kwargs=dict(pk=event.id))
    client.force_login(user)

    response = client.get(url)

    assert response.status_code == 200
    assert response.context['event_video']
    assert response.context['video_duration']
    assert '/subtitles/' in str(response.rendered_content)
    assert '<a href="/export-academy/events/?booking_period=past" class="govuk-link">Back to all events</a>' in str(
        response.rendered_content
    )
    assert 'time' in str(response.rendered_content)
    assert 'Duration:' in str(response.rendered_content)
    assert 'Test event name' in str(response.rendered_content)
    assert 'Test description' in str(response.rendered_content)


@pytest.mark.django_db
def test_event_video_view_with_document(client, user):
    document = wagtail_factories.DocumentFactory(file_size=1395)
    event = factories.EventFactory(name='Test event name', description='Test description', document=document)
    url = reverse('export_academy:event-video', kwargs=dict(pk=event.id))
    client.force_login(user)

    response = client.get(url)

    assert response.status_code == 200
    assert response.context['event_document']
    assert response.context['event_document_size']


@pytest.mark.django_db
def test_event_video_view_with_booking(client, user):
    event = factories.EventFactory(name='Test event name', description='Test description')
    url = reverse('export_academy:event-video', kwargs=dict(pk=event.id))
    registration = factories.RegistrationFactory(email=user.email)
    booking = factories.BookingFactory(event=event, registration=registration, status='Confirmed')
    client.force_login(user)
    client.cookies.load({'cookies_policy': json.dumps({'usage': True})})

    response = client.get(url)

    assert response.status_code == 200
    booking = Booking.objects.get(id=booking.id)
    assert booking.details_viewed is not None
    assert booking.cookies_accepted_on_details_view is True


@pytest.mark.django_db
def test_event_detail_view_no_video(client, user):
    event = factories.EventFactory(video_recording=None)
    url = reverse('export_academy:event-video', kwargs=dict(pk=event.id))
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 200
    assert not response.context.get('event_video')
    assert not response.context.get('video_duration')
    assert 'This video is no longer available.' in str(response.rendered_content)


@pytest.mark.django_db
def test_download_ics(client, user):
    event = factories.EventFactory()
    url = reverse('export_academy:calendar')
    form_data = {'event_id': [event.id]}

    response = client.post(url, form_data)

    assert response.status_code == 200
    content = response.content.decode()
    assert event.name in content


@pytest.mark.django_db
def test_release_views(client, user):
    event = factories.EventFactory(name='Test event name')
    registration = factories.RegistrationFactory(email=user.email)
    url = reverse('export_academy:upcoming-events')

    client.force_login(user)

    factories.BookingFactory(event=event, registration=registration, status='Confirmed')

    response = client.get(url)

    assert 'title="Play recording of Test event name"' not in response.rendered_content


@pytest.mark.django_db
def test_join_redirect(client, user):
    event = factories.EventFactory()
    registration = factories.RegistrationFactory(email=user.email)
    client.force_login(user)
    booking = factories.BookingFactory(event=event, registration=registration, status='Confirmed')
    url = reverse('export_academy:join', kwargs=dict(event_id=event.pk))
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == event.link

    booking = Booking.objects.get(id=booking.id)
    assert booking.status == Booking.JOINED


@pytest.mark.django_db
def test_event_list_for_joined_event(client, user, export_academy_landing_page, test_event_list_hero):
    event = factories.EventFactory()
    registration = factories.RegistrationFactory(email=user.email)
    url = reverse('export_academy:upcoming-events')

    client.force_login(user)

    factories.BookingFactory(event=event, registration=registration, status='Joined')

    response = client.get(url)
    assert response.status_code == 200
    assert event.name in response.rendered_content


@pytest.mark.parametrize(
    'unique_link, expected_page_heading',
    (
        (True, 'Set password for UK Export Academy'),
        (False, 'Join the UK Export Academy'),
    ),
)
@pytest.mark.django_db
def test_sign_up_page(client, unique_link, expected_page_heading, test_unique_link_query_params):
    url = reverse('export_academy:signup')
    if unique_link:
        url += test_unique_link_query_params
    response = client.get(url)
    assert response.status_code == 200
    if unique_link:
        assert response.context['form'].initial['email'] == 'test@example.com'
    assert expected_page_heading in response.content.decode()


@pytest.mark.parametrize(
    'unique_link',
    (
        (True),
        (False),
    ),
)
@pytest.mark.django_db
def test_sign_up_empty_password(client, unique_link, test_unique_link_query_params):
    form_data = {'email': 'test@example.com'}
    url = reverse('export_academy:signup')
    if unique_link:
        url += test_unique_link_query_params
    response = client.post(url, data=form_data)
    assert response.context['form'].errors['password'] == ['Enter a password']
    assert response.status_code == 200
    if unique_link:
        assert response.context['form'].initial['email'] == 'test@example.com'


@pytest.mark.parametrize(
    'user_ea_registered',
    (
        (True),
        (False),
    ),
)
@mock.patch.object(sso_api_client.user, 'create_user')
@pytest.mark.django_db
def test_sign_up_400_error(
    mock_create_user, user_ea_registered, signup_post_request_unique_link, signup_form_post_request_new_user
):
    mock_create_user.return_value = create_response(
        status_code=400, json_body={'password': ["This password contains the word 'password'"]}
    )
    if user_ea_registered:
        response = signup_post_request_unique_link()
    else:
        response = signup_form_post_request_new_user()
    assert response.context['form'].errors['password'] == ["This password contains the word 'password'"]
    assert response.status_code == 200
    if user_ea_registered:
        assert response.context['form'].initial['email'] == 'test@example.com'


@pytest.mark.parametrize(
    'user_ea_registered, expected_query_params',
    (
        (True, '&existing-ea-user=true'),
        (False, ''),
    ),
)
@pytest.mark.django_db
def test_signup_create_password_success(
    mock_create_user_success,
    mock_send_verification_code_email,
    signup_post_request_unique_link,
    signup_form_post_request_new_user,
    uidb64,
    token,
    user_ea_registered,
    expected_query_params,
):
    if user_ea_registered:
        response = signup_post_request_unique_link()
    else:
        response = signup_form_post_request_new_user()

    assert mock_send_verification_code_email.call_count == 1
    assert mock_send_verification_code_email.call_args == mock.call(
        email='test@example.com',
        verification_code={
            'code': '19507',
            'expiration_date': '2023-06-19T11:00:00Z',
        },
        form_url='/export-academy/signup',
        verification_link=(
            f'http://testserver/export-academy/signup/verification?uidb64={uidb64}&token={token}{expected_query_params}'
        ),
        resend_verification_link=('http://testserver/profile/enrol/resend-verification/resend/'),
    )
    assert response.status_code == 302
    assert (
        response['Location']
        == f"{reverse('export_academy:signup-verification')}?uidb64={uidb64}&token={token}{expected_query_params}"
    )


@pytest.mark.parametrize(
    'user_ea_registered, expected_query_params',
    (
        (True, '&existing-ea-user=true'),
        (False, ''),
    ),
)
@mock.patch.object(sso_api_client.user, 'create_user')
@pytest.mark.django_db
def test_sign_up_code_already_sent(
    mock_create_user,
    mock_regenerate_verification_code,
    mock_send_verification_code_email,
    signup_post_request_unique_link,
    signup_form_post_request_new_user,
    user_ea_registered,
    expected_query_params,
):
    uidb64 = 'MjE1ODk1'
    token = 'bq1ftj-e82fb7b694d200b144012bfac0c866b2'
    mock_create_user.return_value = create_response(status_code=409)

    if user_ea_registered:
        response = signup_post_request_unique_link()
    else:
        response = signup_form_post_request_new_user()

    assert mock_send_verification_code_email.call_count == 1
    assert response.status_code == 302
    assert (
        response['Location']
        == f"{reverse('export_academy:signup-verification')}?uidb64={uidb64}&token={token}{expected_query_params}"
    )


@pytest.mark.parametrize(
    'user_ea_registered, expected_query_params',
    (
        (True, 'existing-ea-user=true'),
        (False, ''),
    ),
)
@mock.patch.object(sso_api_client.user, 'create_user')
@mock.patch.object(sso_helpers, 'regenerate_verification_code')
@mock.patch.object(sso_helpers, 'notify_already_registered')
@pytest.mark.django_db
def test_sign_up_already_registered(
    mock_notify_already_registered,
    mock_regenerate_verification_code,
    mock_create_user,
    signup_post_request_unique_link,
    signup_form_post_request_new_user,
    user_ea_registered,
    expected_query_params,
):
    mock_create_user.return_value = create_response(status_code=409)
    mock_regenerate_verification_code.return_value = None

    if user_ea_registered:
        response = signup_post_request_unique_link()
    else:
        response = signup_form_post_request_new_user()

    assert mock_notify_already_registered.call_count == 1
    assert mock_notify_already_registered.call_args == mock.call(
        email='test@example.com', form_url='/export-academy/signup', login_url='http://testserver/export-academy/signin'
    )
    assert response.status_code == 302
    assert response['Location'].startswith(reverse('export_academy:signup-verification'))
    assert expected_query_params in response['Location']


@pytest.mark.parametrize(
    'query_params, user_ea_registered, expected_page_heading',
    (
        ('&existing-ea-user=true', 'true', 'Set password for UK Export Academy'),
        ('', None, 'Join the UK Export Academy'),
    ),
)
@pytest.mark.django_db
def test_verification_page(client, uidb64, token, query_params, user_ea_registered, expected_page_heading):
    response = client.get(
        reverse('export_academy:signup-verification') + f'?uidb64={uidb64}&token={token}{query_params}'
    )
    assert response.status_code == 200
    assert response.context.get('existing_ea_user') == user_ea_registered
    assert expected_page_heading in response.content.decode()


@pytest.mark.django_db
def test_verification_page_no_code(client, uidb64, token):
    response = client.post(reverse('export_academy:signup-verification') + f'?uidb64={uidb64}&token={token}', data={})
    assert response.status_code == 200
    assert response.context['form'].errors['code_confirm'] == ['Enter your confirmation code']


@mock.patch.object(sso_api_client.user, 'verify_verification_code')
@pytest.mark.django_db
def test_verification_page_incorrect_code(mock_verify_verification_code, client, uidb64, token):
    mock_verify_verification_code.return_value = create_response(status_code=400)
    response = client.post(
        reverse('export_academy:signup-verification') + f'?uidb64={uidb64}&token={token}',
        data={'code_confirm': '1234'},
    )
    assert response.status_code == 200
    assert response.context['form'].errors['code_confirm'] == ['This code is incorrect. Please try again.']


@pytest.mark.parametrize(
    'query_params',
    (
        ('&existing-ea-user=true'),
        (''),
    ),
)
@mock.patch.object(sso_api_client.user, 'verify_verification_code')
@pytest.mark.django_db
def test_verification_page_code_expired(
    mock_verify_verification_code,
    mock_regenerate_verification_code,
    mock_send_verification_code_email,
    client,
    uidb64,
    token,
    query_params,
):
    mock_verify_verification_code.return_value = create_response(
        status_code=422, json_body={'email': 'test@example.com'}
    )
    response = client.post(
        reverse('export_academy:signup-verification') + f'?uidb64={uidb64}&token={token}{query_params}',
        data={'code_confirm': '1234'},
    )
    assert response.status_code == 200
    assert mock_regenerate_verification_code.call_count == 1
    assert mock_send_verification_code_email.call_count == 1
    assert mock_send_verification_code_email.call_args == mock.call(
        email='test@example.com',
        verification_code={
            'user_uidb64': 'MjE1ODk1',
            'verification_token': 'bq1ftj-e82fb7b694d200b144012bfac0c866b2',
            'code': '19507',
            'expiration_date': '2023-06-19T11:00:00Z',
        },
        form_url='/export-academy/signup/verification',
        verification_link=(
            f'http://testserver/export-academy/signup/verification?uidb64={uidb64}&token={token}{query_params}'
        ),
        resend_verification_link='http://testserver/profile/enrol/resend-verification/resend/',
    )
    assert response.context['form'].errors['code_confirm'] == ['This code has expired. We have emailed you a new code']


@pytest.mark.parametrize(
    'query_params',
    (
        ('existing-ea-user=true'),
        (''),
    ),
)
@mock.patch.object(sso_helpers, 'set_cookies_from_cookie_jar')
@mock.patch.object(sso_helpers, 'get_cookie_jar')
@mock.patch.object(actions, 'GovNotifyEmailAction')
@mock.patch.object(sso_api_client.user, 'verify_verification_code')
@pytest.mark.django_db
def test_verification_page_success(
    mock_verify_verification_code,
    mock_action_class,
    mock_get_cookie_jar,
    mock_set_cookies_from_cookie_jar,
    client,
    query_params,
):
    mock_verify_verification_code.return_value = create_response(
        status_code=200, json_body={'email': 'test@example.com'}
    )
    response = client.post(
        reverse('export_academy:signup-verification') + f'?uidb64={uidb64}&token={token}&{query_params}',
        data={'code_confirm': '1234'},
    )
    assert mock_action_class.call_count == 1
    assert mock_action_class.call_args == mock.call(
        template_id=settings.GOV_NOTIFY_WELCOME_TEMPLATE_ID,
        email_address='test@example.com',
        form_url='/export-academy/signup/verification',
    )
    assert mock_set_cookies_from_cookie_jar.call_count == 1
    assert response.status_code == 302
    assert response['Location'].startswith(reverse('export_academy:signup-complete'))
    assert query_params in response['Location']


@pytest.mark.parametrize(
    'query_params, user_ea_registered, expected_page_heading',
    (
        ('?existing-ea-user=true', 'true', 'Set password for UK Export Academy'),
        ('', None, 'Join the UK Export Academy'),
    ),
)
@pytest.mark.django_db
def test_signup_complete_page(client, query_params, user_ea_registered, expected_page_heading):
    response = client.get(reverse('export_academy:signup-complete') + query_params)
    assert response.status_code == 200
    assert response.context.get('existing_ea_user') == user_ea_registered
    assert expected_page_heading in response.content.decode()


@pytest.mark.parametrize(
    'unique_link, expected_page_heading',
    (
        (True, 'UK Export Academy on Great.gov.uk'),
        (False, 'Join the UK Export Academy'),
    ),
)
@pytest.mark.django_db
def test_signin_page(client, test_unique_link_query_params, unique_link, expected_page_heading):
    url = reverse('export_academy:signin')
    if unique_link:
        url += test_unique_link_query_params
    response = client.get(url)
    assert response.status_code == 200
    if unique_link:
        assert response.context['form'].initial['email'] == 'test@example.com'
    assert expected_page_heading in response.content.decode()


@pytest.mark.parametrize(
    'unique_link',
    (
        (True),
        (False),
    ),
)
@pytest.mark.django_db
def test_signin_empty_password(client, unique_link, test_unique_link_query_params):
    url = reverse('export_academy:signin')
    if unique_link:
        url += test_unique_link_query_params
    form_data = {'email': 'test@example.com'}
    response = client.post(url, data=form_data)

    assert response.context['form'].errors['password'] == ['Enter a password']
    assert response.status_code == 200
    if unique_link:
        assert response.context['form'].initial['email'] == 'test@example.com'


@pytest.mark.parametrize(
    'unique_link',
    (
        (True),
        (False),
    ),
)
@pytest.mark.django_db
def test_signin_success(client, requests_mock, unique_link, test_unique_link_query_params):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=302)
    form_data = {'email': 'test@example.com', 'password': 'test-password'}

    url = reverse('export_academy:signin')
    if unique_link:
        url += test_unique_link_query_params
    response = client.post(url, data=form_data)

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == 302
    assert response.url == reverse('export_academy:upcoming-events')


@pytest.mark.parametrize(
    'unique_link',
    (
        (True),
        (False),
    ),
)
@pytest.mark.django_db
@mock.patch.object(sso_helpers, 'regenerate_verification_code')
@mock.patch.object(sso_helpers, 'send_verification_code_email')
def test_signin_send_verification(
    mock_send_code, mock_regenerate_code, client, requests_mock, test_unique_link_query_params, unique_link
):
    mock_regenerate_code.return_value = {'code': '12345', 'user_uidb64': 'aBcDe', 'verification_token': '1ab-123abc'}
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=401)
    form_data = {'email': 'test@example.com', 'password': 'test-password'}

    url = reverse('export_academy:signin')
    if unique_link:
        url += test_unique_link_query_params
    response = client.post(url, data=form_data)

    assert mock_send_code.call_count == 1
    assert mock_regenerate_code.call_count == 1
    assert response.status_code == 200


@pytest.mark.parametrize(
    'unique_link',
    (
        (True),
        (False),
    ),
)
@pytest.mark.django_db
def test_signin_invalid_password(client, requests_mock, test_unique_link_query_params, unique_link):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=200)
    form_data = {'email': 'test@example.com', 'password': 'test-password'}

    url = reverse('export_academy:signin')
    if unique_link:
        url += test_unique_link_query_params
    response = client.post(url, data=form_data)

    assert response.context['form'].errors['password'] == ['Invalid email / password']
    assert response.status_code == 200
    if unique_link:
        assert response.context['form'].initial['email'] == 'test@example.com'
