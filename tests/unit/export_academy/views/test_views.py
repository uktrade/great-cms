import pytest
from django.urls import reverse

from export_academy.views import (
    BookingSuccessPageView,
    RegistrationFormView,
    RegistrationSuccessPageView,
)


@pytest.mark.django_db
def test_booking_success_view_response(rf):
    user_email = 'test@test.com'
    request = rf.get(reverse('export_academy:booking-success'))
    request.user = None
    request.session = {'user_email': user_email}
    view = BookingSuccessPageView.as_view()
    response = view(request)
    assert response.status_code == 200
    assert 'Booking confirmation' in response.rendered_content

    # test page redirect if the email doesn't exists in the session
    request.session = {}
    view = BookingSuccessPageView.as_view()
    response = view(request)
    assert response.status_code == 302


@pytest.mark.django_db
def test_registration_view_response(rf):
    user_email = 'test@test.com'
    request = rf.get(reverse('export_academy:registration'))
    request.user = None
    request.session = {'user_email': user_email}
    view = RegistrationFormView.as_view()
    response = view(request)
    assert response.status_code == 200
    assert 'Please enter your details to register for Export Academy' in response.rendered_content


@pytest.mark.django_db
def test_registration_success_view_response(rf):
    user_email = 'test@test.com'
    request = rf.get(reverse('export_academy:registration-success'))
    request.user = None
    request.session = {'user_email': user_email}
    view = RegistrationSuccessPageView.as_view()
    response = view(request)
    assert response.status_code == 200
    assert 'received your registration form' in response.rendered_content

    # test page redirect if the email doesn't exists in the session
    request.session = {}
    view = RegistrationSuccessPageView.as_view()
    response = view(request)
    assert response.status_code == 302
