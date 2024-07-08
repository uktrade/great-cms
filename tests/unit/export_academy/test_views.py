import base64
import hashlib
import json
from datetime import datetime, timedelta
from unittest import mock
from urllib import parse

import factory.fuzzy
import pytest
from directory_forms_api_client import actions
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from wagtail_factories import DocumentFactory

from config import settings
from core import helpers
from core.models import HeroSnippet
from core.snippet_slugs import EA_REGISTRATION_PAGE_HERO
from directory_sso_api_client import sso_api_client
from export_academy.filters import EventFilter
from export_academy.models import Booking, Registration, VideoOnDemandPageTracking
from export_academy.views import (
    CsatUserFeedback,
    EventsDetailsView,
    EventVideoOnDemandView,
)
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
def next_url():
    event = factories.EventFactory()
    return event.get_absolute_url()


@pytest.fixture
def test_unique_link_query_params():
    registration = Registration(first_name='test', last_name='test', email='test@example.com', external_id='123456789')
    registration.save()
    idb64 = base64.b64encode(bytes(registration.external_id, 'utf-8'))
    token = hashlib.sha256(registration.email.encode('UTF-8')).hexdigest()
    return f'?idb64={idb64.decode("utf-8")}&token={token}'


@pytest.fixture
def signup_post_request_unique_link(client, test_unique_link_query_params):
    form_data = {'email': 'test@example.com', 'password': 'newPassword', 'mobile_phone_number': ''}

    def post_request():
        return client.post(reverse('export_academy:signup') + test_unique_link_query_params, data=form_data)

    return post_request


@pytest.fixture
def signup_form_post_request_new_user(client):
    form_data = {'email': 'test@example.com', 'password': 'newPassword', 'mobile_phone_number': ''}

    def post_request():
        return client.post(reverse('export_academy:signup'), data=form_data)

    return post_request


@pytest.fixture
def signup_post_request_unique_link_with_next(client, test_unique_link_query_params, next_url):
    form_data = {'email': 'test@example.com', 'password': 'newPassword', 'mobile_phone_number': ''}

    def post_request():
        return client.post(
            reverse('export_academy:signup') + test_unique_link_query_params + f'&next={next_url}', data=form_data
        )

    return post_request


@pytest.fixture
def signup_form_post_request_new_user_with_next(client, next_url):
    form_data = {'email': 'test@example.com', 'password': 'newPassword', 'mobile_phone_number': ''}

    def post_request():
        return client.post(reverse('export_academy:signup') + f'?next={next_url}', data=form_data)

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

    url = reverse('export_academy:booking-success', kwargs={'booking_id': booking.id})
    response = client.get(url)

    assert response.status_code == 200
    assert text in response.rendered_content


@pytest.mark.parametrize(
    'booking_status,success_url,text',
    ((Booking.CONFIRMED, 'export_academy:booking-success', 'Booking confirmed'),),
)
@pytest.mark.django_db
def test_csat_user_feedback_with_session_value(
    export_academy_landing_page, test_event_list_hero, client, user, booking_status, success_url, text
):
    client.force_login(user)
    registration = factories.RegistrationFactory(email=user.email)
    event = factories.EventFactory()
    booking = factories.BookingFactory(event=event, status=booking_status, registration=registration)
    url = reverse('export_academy:booking-success', kwargs={'booking_id': booking.id})

    CsatUserFeedback.objects.create(id=1, URL='http://test.com')
    session = client.session
    session['ukea_csat_id'] = 1
    session.save()
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'booking_status,success_url,text',
    ((Booking.CONFIRMED, 'export_academy:booking-success', 'Booking confirmed'),),
)
@pytest.mark.django_db
def test_csat_user_feedback_submit(
    export_academy_landing_page, test_event_list_hero, client, user, booking_status, success_url, text
):
    client.force_login(user)
    registration = factories.RegistrationFactory(email=user.email)
    event = factories.EventFactory()
    booking = factories.BookingFactory(event=event, status=booking_status, registration=registration)
    url = reverse('export_academy:booking-success', kwargs={'booking_id': booking.id})

    CsatUserFeedback.objects.create(id=1, URL='http://test.com')
    session = client.session
    session['ukea_csat_id'] = 1
    session['user_journey'] = 'DASHBOARD'
    session.save()
    response = client.post(
        url,
        {
            'satisfaction': 'SATISFIED',
            'user_journey': 'DASHBOARD',
            'experience': ['NOT_FIND_LOOKING_FOR'],
            'likelihood_of_return': 'LIKELY',
        },
    )
    assert response.status_code == 302


@pytest.mark.parametrize(
    'booking_status,success_url,text',
    ((Booking.CONFIRMED, 'export_academy:booking-success', 'Booking confirmed'),),
)
@pytest.mark.django_db
def test_csat_user_feedback_submit_with_javascript(
    export_academy_landing_page, test_event_list_hero, client, user, booking_status, success_url, text
):
    client.force_login(user)
    registration = factories.RegistrationFactory(email=user.email)
    event = factories.EventFactory()
    booking = factories.BookingFactory(event=event, status=booking_status, registration=registration)
    url = reverse('export_academy:booking-success', kwargs={'booking_id': booking.id}) + '?js_enabled=True'

    CsatUserFeedback.objects.create(id=1, URL='http://test.com')
    session = client.session
    session['ukea_csat_id'] = 1
    session['user_journey'] = 'DASHBOARD'
    session.save()
    response = client.post(
        url,
        {
            'satisfaction': 'SATISFIED',
            'user_journey': 'DASHBOARD',
            'experience': ['NOT_FIND_LOOKING_FOR'],
            'likelihood_of_return': 'LIKELY',
        },
    )
    assert response.status_code == 200


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
                'first_name': 'Enter your first name',
                'last_name': 'Enter your last name',
                'job_title': 'Enter your job title',
                'phone_number': 'Enter your telephone number',
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
                'export_experience': 'Choose one option about your export experience',
                'sector': 'Choose a sector',
                'export_product': 'Choose one option about what you export',
            },
        ),
        (
            reverse('export_academy:registration-business'),
            {
                'business_name': 'Test Business',
                'business_address_line_1': '1 Main Street',
                'business_postcode': 'SW1A 1AA',
                'annual_turnover': 'Up to £85,000',
                'employee_count': '10 to 49',
            },
            reverse('export_academy:registration-marketing'),
            {
                'business_name': 'Enter your business name',
                'business_address_line_1': 'Enter the first line of your business address',
                'business_postcode': 'Enter your business postcode',
                'annual_turnover': 'Enter a turnover amount',
                'employee_count': 'Choose number of employees',
            },
        ),
        (
            reverse('export_academy:registration-marketing'),
            {
                'marketing_sources': 'From an International Trade Advisor in my region',
                'marketing_sources_other': '',
            },
            reverse('export_academy:registration-confirm'),
            {
                'marketing_sources': 'Enter how you heard about the UK Export Academy',
                'marketing_sources_other': 'Enter how you heard about the UK Export Academy',
            },
        ),
        (
            reverse('export_academy:registration-marketing'),
            {
                'marketing_sources': 'Other',
                'marketing_sources_other': 'Postbox',
            },
            reverse('export_academy:registration-confirm'),
            {
                'marketing_sources': 'Enter how you heard about the UK Export Academy',
                'marketing_sources_other': 'Enter how you heard about the UK Export Academy',
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

    #   Redirect succeeds with valid data
    response = client.post(page_url, form_data)
    assert response.status_code == 302
    assert response.url == redirect_url

    #   When editing registration details the redirect returns to the confirm page
    edit_page_url = page_url + 'edit/'
    assert client.get(edit_page_url).context['button_text'] == 'Save'
    response = client.post(edit_page_url, form_data)
    assert response.status_code == 302
    assert response.url == reverse('export_academy:registration-confirm')

    if page_url == reverse('export_academy:registration-marketing') and form_data['marketing_sources'] != 'Other':
        pytest.skip('marketing_sources_other is an optional field if marketing_sources is not other')

    #   Redirect fails when any of the fields in the form are missing
    invalid_form_data = form_data.copy()
    for key in form_data:
        invalid_form_data.pop(key)
        response = client.post(page_url, invalid_form_data)
        assert response.status_code == 200
        assert error_messages[key] in str(response.rendered_content)
        invalid_form_data = form_data.copy()


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
def test_event_video_view_redirect_for_unauthenticated_user(client, user):
    event = factories.EventFactory(name='Test event name', description='Test description')
    url = reverse('export_academy:event-video', kwargs=dict(pk=event.id))
    response = client.get(url)
    assert response.status_code == 302
    assert response.url == event.get_absolute_url()


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
    assert 'time' in str(response.rendered_content)
    assert 'Duration:' in str(response.rendered_content)
    assert 'Test event name' in str(response.rendered_content)
    assert 'Test description' in str(response.rendered_content)


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
def test_event_video_view_no_video(client, user):
    event = factories.EventFactory(video_recording=None)
    url = reverse('export_academy:event-video', kwargs=dict(pk=event.id))
    client.force_login(user)
    response = client.get(url)

    assert response.status_code == 404
    assert not response.context.get('event_video')
    assert not response.context.get('video_duration')


@pytest.mark.django_db
def test_event_video_view_with_video_and_document(client, user, test_uuid):
    document = DocumentFactory()
    event = factories.EventFactory(name='Test event name', description='Test description', document=document)
    url = reverse('export_academy:event-video', kwargs=dict(pk=event.id))
    client.force_login(user)

    response = client.get(url)

    assert response.status_code == 200
    assert response.context['event_document_size']
    assert response.context['event_document_url']


@pytest.mark.django_db
def test_event_video_view_with_video_no_document(client, user, test_uuid):
    event = factories.EventFactory(name='Test event name', description='Test description', document=None)
    url = reverse('export_academy:event-video', kwargs=dict(pk=event.id))
    client.force_login(user)

    response = client.get(url)

    assert response.status_code == 200
    assert not response.context.get('event_document_size')
    assert not response.context.get('event_document_url')
    assert response.context['event_video']
    assert response.context['video_duration']


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
    form_data = {'email': 'test@example.com', 'mobile_phone_number': ''}
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
    'query_params, user_ea_registered, next',
    (
        ('&next=next_url&existing-ea-user=true', 'true', 'next_url'),
        ('&existing-ea-user=true', 'true', None),
        ('&next=next_url', None, 'next_url'),
        ('', None, None),
    ),
)
@pytest.mark.django_db
def test_signup_create_password_success(
    mock_create_user_success,
    mock_send_verification_code_email,
    uidb64,
    token,
    next_url,
    signup_post_request_unique_link,
    signup_post_request_unique_link_with_next,
    signup_form_post_request_new_user,
    signup_form_post_request_new_user_with_next,
    query_params,
    user_ea_registered,
    next,
):
    if user_ea_registered:
        response = signup_post_request_unique_link() if not next else signup_post_request_unique_link_with_next()
    else:
        response = signup_form_post_request_new_user() if not next else signup_form_post_request_new_user_with_next()

    query_params = query_params.replace('next_url', next_url)

    assert mock_send_verification_code_email.call_count == 1
    assert mock_send_verification_code_email.call_args == mock.call(
        email='test@example.com',
        verification_code={
            'code': '19507',
            'expiration_date': '2023-06-19T11:00:00Z',
        },
        form_url='/export-academy/signup',
        verification_link=(
            f'http://testserver/export-academy/signup/verification?uidb64={uidb64}&token={token}{query_params}'
        ),
        resend_verification_link=('http://testserver/profile/enrol/resend-verification/resend/'),
    )
    assert response.status_code == 302

    response_location_url = response['Location'].split('?')[0]
    assert response_location_url == reverse('export_academy:signup-verification')
    response_location_params = dict(parse.parse_qsl(parse.urlsplit(response['Location']).query))
    assert response_location_params == dict(parse.parse_qsl(f'uidb64={uidb64}&token={token}{query_params}'))


@pytest.mark.parametrize(
    'query_params, user_ea_registered, next',
    (
        ('&next=next_url&existing-ea-user=true', 'true', 'next_url'),
        ('&existing-ea-user=true', 'true', None),
        ('&next=next_url', None, 'next_url'),
        ('', None, None),
    ),
)
@mock.patch.object(sso_api_client.user, 'create_user')
@pytest.mark.django_db
def test_sign_up_code_already_sent(
    mock_create_user,
    mock_regenerate_verification_code,
    mock_send_verification_code_email,
    next_url,
    signup_post_request_unique_link,
    signup_post_request_unique_link_with_next,
    signup_form_post_request_new_user,
    signup_form_post_request_new_user_with_next,
    query_params,
    user_ea_registered,
    next,
):
    uidb64 = 'MjE1ODk1'
    token = 'bq1ftj-e82fb7b694d200b144012bfac0c866b2'
    mock_create_user.return_value = create_response(status_code=409)

    if user_ea_registered:
        response = signup_post_request_unique_link() if not next else signup_post_request_unique_link_with_next()
    else:
        response = signup_form_post_request_new_user() if not next else signup_form_post_request_new_user_with_next()

    query_params = query_params.replace('next_url', next_url)

    assert mock_send_verification_code_email.call_count == 1
    assert response.status_code == 302

    response_location_url = response['Location'].split('?')[0]
    assert response_location_url == reverse('export_academy:signup-verification')
    response_location_params = dict(parse.parse_qsl(parse.urlsplit(response['Location']).query))
    assert response_location_params == dict(parse.parse_qsl(f'uidb64={uidb64}&token={token}{query_params}'))


@pytest.mark.parametrize(
    'query_params, user_ea_registered, next',
    (
        ('next=next_url&existing-ea-user=true', 'true', 'next_url'),
        ('existing-ea-user=true', 'true', None),
        ('next=next_url', None, 'next_url'),
        ('', None, None),
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
    next_url,
    signup_post_request_unique_link,
    signup_post_request_unique_link_with_next,
    signup_form_post_request_new_user,
    signup_form_post_request_new_user_with_next,
    query_params,
    user_ea_registered,
    next,
):
    mock_create_user.return_value = create_response(status_code=409)
    mock_regenerate_verification_code.return_value = None

    if user_ea_registered:
        response = signup_post_request_unique_link() if not next else signup_post_request_unique_link_with_next()
    else:
        response = signup_form_post_request_new_user() if not next else signup_form_post_request_new_user_with_next()

    query_params = query_params.replace('next_url', next_url)

    assert mock_notify_already_registered.call_count == 1
    assert mock_notify_already_registered.call_args == mock.call(
        email='test@example.com', form_url='/export-academy/signup', login_url='http://testserver/export-academy/signin'
    )
    assert response.status_code == 302
    response_location_url = response['Location'].split('?')[0]
    assert response_location_url == reverse('export_academy:signup-verification')


@pytest.mark.parametrize(
    'query_params, user_ea_registered, expected_page_heading',
    (
        ('&next=next_url&existing-ea-user=true', 'true', 'Set password for UK Export Academy'),
        ('&existing-ea-user=true', 'true', 'Set password for UK Export Academy'),
        ('&next=next_url', None, 'Join the UK Export Academy'),
        ('', None, 'Join the UK Export Academy'),
    ),
)
@pytest.mark.django_db
def test_verification_page(client, uidb64, token, next_url, query_params, user_ea_registered, expected_page_heading):
    query_params = query_params.replace('next_url', next_url)
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
    (('&next=next_url&existing-ea-user=true'), ('&next=next_url'), ('')),
)
@mock.patch.object(sso_api_client.user, 'verify_verification_code')
@pytest.mark.django_db
def test_verification_page_code_expired(
    mock_verify_verification_code,
    mock_regenerate_verification_code,
    mock_send_verification_code_email,
    next_url,
    client,
    uidb64,
    token,
    query_params,
):
    mock_verify_verification_code.return_value = create_response(
        status_code=422, json_body={'email': 'test@example.com'}
    )
    query_params = query_params.replace('next_url', next_url)
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
    (('next=next_url&existing-ea-user=true'), ('next=next_url'), ('')),
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
    next_url,
    query_params,
):
    mock_verify_verification_code.return_value = create_response(
        status_code=200, json_body={'email': 'test@example.com'}
    )
    query_params = query_params.replace('next_url', next_url)
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

    response_location_url = response['Location'].split('?')[0]
    assert response_location_url == reverse('export_academy:signup-complete')
    response_location_params = dict(parse.parse_qsl(parse.urlsplit(response['Location']).query))
    assert response_location_params == dict(parse.parse_qsl(query_params))


@pytest.mark.parametrize(
    'query_params, user_ea_registered, expected_page_heading',
    (
        ('?next=next_url&existing-ea-user=true', 'true', 'Set password for UK Export Academy'),
        ('?existing-ea-user=true', 'true', 'Set password for UK Export Academy'),
        ('?next=next_url', None, 'Join the UK Export Academy'),
        ('', None, 'Join the UK Export Academy'),
    ),
)
@pytest.mark.django_db
def test_signup_complete_page(client, next_url, query_params, user_ea_registered, expected_page_heading):
    query_params = query_params.replace('next_url', next_url)
    response = client.get(reverse('export_academy:signup-complete') + query_params)
    assert response.status_code == 200
    assert response.context.get('existing_ea_user') == user_ea_registered
    assert expected_page_heading in response.content.decode()


@pytest.mark.parametrize(
    'unique_link, query_params, next, expected_page_heading',
    (
        (True, '?next=next_url', 'next_url', 'UK Export Academy on Great.gov.uk'),
        (True, '', None, 'UK Export Academy on Great.gov.uk'),
        (False, '?next=next_url', 'next_url', 'Join the UK Export Academy'),
        (False, '', None, 'Join the UK Export Academy'),
    ),
)
@pytest.mark.django_db
def test_signin_page(
    client, test_unique_link_query_params, next_url, unique_link, query_params, next, expected_page_heading
):
    url = reverse('export_academy:signin')
    query_params = query_params.replace('next_url', next_url)
    if unique_link:
        url += test_unique_link_query_params
        if next:
            url += query_params.replace('?', '&')
    elif next:
        url += query_params
    response = client.get(url)
    assert response.status_code == 200
    if unique_link:
        assert response.context['form'].initial['email'] == 'test@example.com'
    assert expected_page_heading in response.content.decode()


@pytest.mark.parametrize(
    'unique_link, query_params, next',
    (
        (True, '?next=next_url', 'next_url'),
        (True, '', None),
        (False, '?next=next_url', 'next_url'),
        (False, '', None),
    ),
)
@pytest.mark.django_db
def test_signin_empty_password(client, next_url, unique_link, query_params, next, test_unique_link_query_params):
    url = reverse('export_academy:signin')
    query_params = query_params.replace('next_url', next_url)
    if unique_link:
        url += test_unique_link_query_params
        if next:
            url += query_params.replace('?', '&')
    elif next:
        url += query_params
    form_data = {'email': 'test@example.com'}
    response = client.post(url, data=form_data)

    assert response.context['form'].errors['password'] == ['Enter a password']
    assert response.status_code == 200
    if unique_link:
        assert response.context['form'].initial['email'] == 'test@example.com'


@pytest.mark.parametrize(
    'unique_link, query_params, next',
    (
        (True, '?next=next_url', 'next_url'),
        (True, '', None),
        (False, '?next=next_url', 'next_url'),
        (False, '', None),
    ),
)
@pytest.mark.django_db
def test_signin_success(
    client, next_url, requests_mock, unique_link, query_params, next, test_unique_link_query_params
):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=302)
    form_data = {'email': 'test@example.com', 'password': 'test-password'}

    url = reverse('export_academy:signin')
    query_params = query_params.replace('next_url', next_url)
    if unique_link:
        url += test_unique_link_query_params
        if next:
            url += query_params.replace('?', '&')
    elif next:
        url += query_params
    response = client.post(url, data=form_data)

    redirect_url = reverse('export_academy:upcoming-events') if not next else next_url

    assert isinstance(response, HttpResponseRedirect)
    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.parametrize(
    'unique_link, query_params, next',
    (
        (True, '?next=next_url', 'next_url'),
        (True, '', None),
        (False, '?next=next_url', 'next_url'),
        (False, '', None),
    ),
)
@pytest.mark.django_db
@mock.patch.object(sso_helpers, 'regenerate_verification_code')
@mock.patch.object(sso_helpers, 'send_verification_code_email')
def test_signin_send_verification(
    mock_send_code,
    mock_regenerate_code,
    client,
    next_url,
    requests_mock,
    test_unique_link_query_params,
    unique_link,
    query_params,
    next,
):
    mock_regenerate_code.return_value = {'code': '12345', 'user_uidb64': 'aBcDe', 'verification_token': '1ab-123abc'}
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=401)
    form_data = {'email': 'test@example.com', 'password': 'test-password'}

    url = reverse('export_academy:signin')
    query_params = query_params.replace('next_url', next_url)
    if unique_link:
        url += test_unique_link_query_params
        if next:
            url += query_params.replace('?', '&')
    elif next:
        url += query_params
    response = client.post(url, data=form_data)

    assert mock_send_code.call_count == 1
    assert mock_regenerate_code.call_count == 1
    assert response.status_code == 200


@pytest.mark.parametrize(
    'unique_link, query_params, next',
    (
        (True, '?next=next_url', 'next_url'),
        (True, '', None),
        (False, '?next=next_url', 'next_url'),
        (False, '', None),
    ),
)
@pytest.mark.django_db
def test_signin_invalid_password(
    client, next_url, requests_mock, test_unique_link_query_params, unique_link, query_params, next
):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=200)
    form_data = {'email': 'test@example.com', 'password': 'test-password'}

    url = reverse('export_academy:signin')
    query_params = query_params.replace('next_url', next_url)
    if unique_link:
        url += test_unique_link_query_params
        if next:
            url += query_params.replace('?', '&')
    elif next:
        url += query_params
    response = client.post(url, data=form_data)

    assert response.context['form'].errors['password'] == [
        """The email or password you entered is not correct.
        If you've forgotten your password, you can reset it"""
    ]
    assert response.status_code == 200
    if unique_link:
        assert response.context['form'].initial['email'] == 'test@example.com'


class EventsDetailsViewTestCase(TestCase):
    @pytest.fixture(autouse=True)
    def set_fixtures(self, user):
        self.user = user

    def setUp(self):
        now = timezone.now()
        self.event_with_video = factories.EventFactory(completed=None)
        self.event_without_video = factories.EventFactory(completed=None, video_recording=None)
        self.event_with_video_and_completed = factories.EventFactory()
        self.past_event = factories.EventFactory(
            start_date=now - timedelta(hours=6),
            end_date=now - timedelta(hours=5),
            completed=None,
            name='Test event name',
        )

    def test_get_warning_text_event_not_ended_and_not_completed(self):
        view = EventsDetailsView()
        view.event = self.event_with_video
        view.ended = False
        view.has_video = True
        view.signed_in = True
        view.booked = True

        warning_text = view.get_warning_text()
        expected_text = ''
        self.assertEqual(warning_text, expected_text)

    def test_get_warning_text_event_ended_no_video(self):
        view = EventsDetailsView()
        view.event = self.event_without_video
        view.ended = True
        view.has_video = False
        view.signed_in = True
        view.booked = True

        warning_text = view.get_warning_text()

        expected_text = 'This event has ended.'
        self.assertEqual(warning_text, expected_text)

    def test_get_warning_text_event_ended_with_video_not_signed_in(self):
        view = EventsDetailsView()
        view.event = self.event_with_video
        view.ended = True
        view.has_video = True
        view.signed_in = False
        view.booked = True

        warning_text = view.get_warning_text()

        expected_text_1 = 'This event has ended.'
        expected_text_2 = ' Event recordings are only available for attendees to view for 4 weeks after the event.'
        self.assertEqual(warning_text, expected_text_1 + expected_text_2)

    def test_get_warning_text_event_completed(self):
        view = EventsDetailsView()
        view.event = self.event_with_video_and_completed
        view.ended = False
        view.has_video = True
        view.signed_in = True
        view.booked = True
        view.event.completed = True

        warning_text = view.get_warning_text()

        expected_text = 'This event has ended. Event recordings are only available for 4 weeks after the event.'
        self.assertEqual(warning_text, expected_text)

    def test_get_warning_text_event_closed(self):
        view = EventsDetailsView()
        view.event = self.event_with_video
        view.ended = False
        view.has_video = True
        view.signed_in = True
        view.booked = True
        view.event.closed = True

        warning_text = view.get_warning_text()

        expected_text = ''
        self.assertEqual(warning_text, expected_text)

    def test_get_warning_message_with_signed_in_with_video_and_not_booked(self):
        view = EventsDetailsView()
        view.event = self.event_with_video
        view.ended = True
        view.has_video = True
        view.signed_in = True
        view.booked = False
        warning_text = view.get_warning_text()
        expected_text = 'This event has ended.'
        self.assertEqual(warning_text, expected_text)

    def test_get_warning_call_to_action_event_ended_with_video_signed_in_and_booked(self):
        view = EventsDetailsView()
        view.event = self.event_with_video_and_completed
        view.ended = False
        view.has_video = True
        view.signed_in = True
        view.booked = True

        call_to_action = view.get_warning_call_to_action()
        assert 'Watch <span class="govuk-visually-hidden">event recording</span>now</a>' in call_to_action

    def test_get_warning_call_to_action_event_ended_with_video_signed_in_and_booked_and_not_completed(self):
        view = EventsDetailsView()
        view.event = self.event_with_video
        view.ended = True
        view.has_video = True
        view.signed_in = True
        view.booked = True
        call_to_action = view.get_warning_call_to_action()

        assert 'Watch <span class="govuk-visually-hidden">event recording</span>now</a>' in call_to_action

    def test_event_has_ended(self):
        view = EventsDetailsView()
        view.event = self.past_event

    def test_view_context(self):
        url = self.event_with_video_and_completed.get_absolute_url()
        request = self.client.get(url)
        view = EventsDetailsView(request=request)
        context = view.request.context_data

        self.assertTrue('ended' in context)
        self.assertTrue('has_video' in context)
        self.assertTrue('event_types' in context)
        self.assertTrue('speakers' in context)
        self.assertTrue('signed_in' in context)
        self.assertTrue('booked' in context)
        self.assertTrue('warning_text' in context)
        self.assertTrue('warning_call_to_action' in context)
        self.assertTrue('has_event_badges' in context)

        self.assertEqual(context['ended'], False)
        self.assertEqual(context['booked'], False)
        self.assertEqual(context['has_video'], True)
        self.assertEqual(len(context['speakers']), 0)
        self.assertEqual(len(context['event_types']), 0)
        self.assertEqual(context['signed_in'], False)
        self.assertTrue('This event has ended.' in context['warning_text'])
        self.assertTrue('Sign in' in context['warning_call_to_action'])
        self.assertTrue(context['has_event_badges'])

    def tearDown(self):
        self.event_with_video.delete()
        self.event_with_video_and_completed.delete()
        self.event_without_video.delete()


@pytest.mark.django_db
def test_course_page(client, root_page):
    course_page = factories.CoursePageFactory(parent=root_page)
    course_events = factories.EventsOnCourseFactory(page_id=course_page.id)

    # create events
    latest_event = factories.EventFactory(start_date=timezone.now() + timedelta(days=1))
    factories.ModuleEventSetFactory(page_id=course_events.id, event_id=latest_event.id)

    later_event = factories.EventFactory(start_date=timezone.now() + timedelta(days=2))
    factories.ModuleEventSetFactory(page_id=course_events.id, event_id=later_event.id)

    past_event = factories.EventFactory(start_date=timezone.now() - timedelta(days=2))
    factories.ModuleEventSetFactory(page_id=course_events.id, event_id=past_event.id)

    url = reverse('export_academy:course', kwargs=dict(slug=course_page.slug))
    response = client.get(url)
    assert response.status_code == 200
    assert latest_event.name in response.rendered_content


@pytest.mark.django_db
def test_course_page_returns_404_for_slug_not_found(client):
    url = reverse('export_academy:course', kwargs=dict(slug=factory.fuzzy.FuzzyText(length=50).fuzz()))
    response = client.get(url)
    assert response.status_code == 404


class EventVideoOnDemandViewTest(TestCase):
    @pytest.fixture(autouse=True)
    def set_fixtures(self, user, root_page, rf, client):
        self.user = user
        self.root_page = root_page
        self.rf = rf
        self.client = client
        self.USER_EMAIL = 'joe.bloggs@gmail.com'

    def setUp(self):
        self.video = factories.GreatMediaFactory()
        self.past_event_date = datetime(2023, 9, 13)
        self.event = factories.EventFactory(
            slug='event-slug-17-october-2023',
            start_date=timezone.now() + timedelta(hours=6),
        )
        self.event_with_past_event = factories.EventFactory(
            slug='event-slug2-17-october-2023',
            past_event_recorded_date=self.past_event_date,
            start_date=timezone.now() + timedelta(hours=6),
        )
        self.past_event = factories.EventFactory(
            slug='event-slug3-13-september-2023',
            past_event_video_recording=self.video,
            past_event_recorded_date=self.past_event_date,
        )
        self.event_with_no_recording = factories.EventFactory(
            past_event_video_recording=None,
            past_event_recorded_date=None,
        )
        self.event_with_incorrect_slug = factories.EventFactory(
            slug='event-slug',
        )
        self.course_page = factories.CoursePageFactory(
            parent=self.root_page,
            page_heading='essentials_title',
        )
        course_events = factories.EventsOnCourseFactory(
            page_id=self.course_page.id,
        )
        factories.ModuleEventSetFactory(
            page_id=course_events.id,
            event_id=self.event_with_past_event.id,
        )

    def test_extract_date_and_event_name(self):
        view = EventVideoOnDemandView()
        input_string = 'event-slug-12-September-2023'
        text_before_date, date = view.extract_date_and_event_name(input_string)
        self.assertEqual(text_before_date, 'event-slug')
        self.assertEqual(date, '12-September-2023')

    def test_get_object(self):
        view = EventVideoOnDemandView()
        slug = 'event-slug2-13-September-2023'
        view.kwargs = {'slug': slug}
        recorded_date = self.past_event_date.date()
        self.event.past_event_recorded_date = recorded_date
        obj = view.get_object()
        self.assertEqual(obj.slug, self.event_with_past_event.slug)
        self.assertEqual(obj.name, self.event_with_past_event.name)

    def test_get_context_data(self):
        self.client.login(username='testuser', password='testpassword')
        url = reverse('export_academy:video-on-demand', kwargs={'slug': self.event.get_past_event_recording_slug()})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('event_video', response.context)
        self.assertIn('video_duration', response.context)
        self.assertIn('speakers', response.context)
        self.assertIn('event_types', response.context)
        self.assertIn('signed_in', response.context)
        self.assertIn('event', response.context)
        self.assertIn('series', response.context)
        self.assertIn('slug', response.context)
        self.assertIn('video_page_slug', response.context)

    def test_get_past_event_recording_slug_is_none(self):
        self.assertIsNone(self.event_with_no_recording.get_past_event_recording_slug())
        self.assertIsNone(self.event_with_incorrect_slug.get_past_event_recording_slug())

    def test_get_course_page_details(self):
        self.assertEqual(self.event_with_no_recording.get_course(), [])
        self.assertEqual(
            self.event_with_past_event.get_course(), [{'label': 'essentials_title', 'value': 'essentials'}]
        )

    @mock.patch.object(VideoOnDemandPageTracking, 'save')
    def test_get_logged_in_user(self, mock_tracking_save):
        self.client.force_login(self.user)
        kwargs = {'slug': self.past_event.get_past_event_recording_slug()}
        url = reverse('export_academy:video-on-demand', kwargs=kwargs)
        request = self.rf.get(url)
        request.user = self.user
        response = EventVideoOnDemandView.as_view(
            event=self.past_event, video=self.past_event.past_event_video_recording
        )(request, **kwargs)
        assert response.status_code == 200
        assert mock_tracking_save.call_count == 1

    @mock.patch.object(VideoOnDemandPageTracking, 'save')
    def test_get_logged_in_user_not_business_sso_user(self, mock_tracking_save):
        user = get_user_model().objects.create_user('alice', 'alice@example.com', 'password')
        self.client.force_login(user)
        kwargs = {'slug': self.past_event.get_past_event_recording_slug()}
        url = reverse('export_academy:video-on-demand', kwargs=kwargs)
        request = self.rf.get(url)
        request.user = user
        response = EventVideoOnDemandView.as_view(
            event=self.past_event, video=self.past_event.past_event_video_recording
        )(request, **kwargs)
        assert response.status_code == 200
        assert mock_tracking_save.call_count == 1

    @mock.patch.object(VideoOnDemandPageTracking, 'save')
    def test_get_logged_in_user_with_company_details(self, mock_tracking_save):
        self.client.force_login(self.user)
        kwargs = {'slug': self.past_event.get_past_event_recording_slug()}
        url = reverse('export_academy:video-on-demand', kwargs=kwargs)
        request = self.rf.get(url)
        company = {'name': 'FRED BLOGS', 'registered_office_address': {'postal_code': 'W1AA 1AA'}}
        self.user.company = helpers.CompanyParser(company)
        request.user = self.user

        response = EventVideoOnDemandView.as_view(
            event=self.past_event, video=self.past_event.past_event_video_recording
        )(request, **kwargs)
        assert response.status_code == 200
        assert mock_tracking_save.call_count == 1

    @mock.patch.object(EventVideoOnDemandView, '_get_location')
    @mock.patch.object(VideoOnDemandPageTracking, 'save')
    def test_get_logged_in_user_with_region(self, mock_tracking_save, mock_get_location):
        self.client.force_login(self.user)
        kwargs = {'slug': self.past_event.get_past_event_recording_slug()}
        url = reverse('export_academy:video-on-demand', kwargs=kwargs)
        request = self.rf.get(url)
        request.user = self.user
        mock_get_location.return_value = {'region': 'ENG'}
        response = EventVideoOnDemandView.as_view(
            event=self.past_event, video=self.past_event.past_event_video_recording
        )(request, **kwargs)
        assert response.status_code == 200
        assert mock_tracking_save.call_count == 1

    @mock.patch.object(VideoOnDemandPageTracking, 'save')
    def test_get_logged_in_user_with_registration_and_booking(self, mock_tracking_save):
        self.client.force_login(self.user)
        kwargs = {'slug': self.past_event.get_past_event_recording_slug()}
        url = reverse('export_academy:video-on-demand', kwargs=kwargs)
        request = self.rf.get(url)
        request.user = self.user
        registration = factories.RegistrationFactory(email=self.user.email)
        factories.BookingFactory(event=self.past_event, registration=registration)
        response = EventVideoOnDemandView.as_view(
            event=self.past_event, video=self.past_event.past_event_video_recording
        )(request, **kwargs)
        assert response.status_code == 200
        assert mock_tracking_save.call_count == 1

    @mock.patch.object(VideoOnDemandPageTracking, 'save')
    def test_get_logged_in_user_with_registration_and_no_booking(self, mock_tracking_save):
        self.client.force_login(self.user)
        kwargs = {'slug': self.past_event.get_past_event_recording_slug()}
        url = reverse('export_academy:video-on-demand', kwargs=kwargs)
        request = self.rf.get(url)
        request.user = self.user
        factories.RegistrationFactory(email=self.user.email)
        response = EventVideoOnDemandView.as_view(
            event=self.past_event, video=self.past_event.past_event_video_recording
        )(request, **kwargs)
        assert response.status_code == 200
        assert mock_tracking_save.call_count == 1

    def test_get_logged_in_user_already_tracked(self):
        kwargs = {'slug': self.past_event.get_past_event_recording_slug()}
        self.user.email = self.USER_EMAIL
        VideoOnDemandPageTracking.objects.create(
            user_email=self.USER_EMAIL,
            event=self.past_event,
            video=self.past_event.past_event_video_recording,
        )
        self.client.force_login(self.user)
        url = reverse('export_academy:video-on-demand', kwargs=kwargs)
        request = self.rf.get(url)
        request.user = self.user
        response = EventVideoOnDemandView.as_view(event=self.past_event)(request, **kwargs)
        assert response.status_code == 200
        video_on_demand_page_tracking = VideoOnDemandPageTracking.objects.filter(
            user_email=self.user.email, event=self.past_event, video=self.past_event.past_event_video_recording
        )
        assert video_on_demand_page_tracking.count() == 1

    def test_get_logged_out_user(self):
        kwargs = kwargs = {'slug': self.past_event.slug}
        url = reverse('export_academy:video-on-demand', kwargs=kwargs)
        request = self.rf.get(url)
        user_not_logged_in = type(
            'obj',
            (object,),
            {'is_authenticated': False},
        )
        request.user = user_not_logged_in
        response = EventVideoOnDemandView.as_view(event=self.past_event)(request, **kwargs)
        assert response.status_code == 200
