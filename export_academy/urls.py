from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, reverse_lazy

from core.urls import SIGNUP_URL
from export_academy import helpers, views

app_name = 'export_academy'


def registration_required(function):
    inner = user_passes_test(
        lambda user: helpers.is_export_academy_registered(user),
        reverse_lazy('export_academy:registration'),
        None,
    )
    return inner(function)


urlpatterns = [
    path(
        'upcoming-events/',
        views.EventListView.as_view(),
        name='upcoming-events',
    ),
    path(
        'registration/', login_required(views.RegistrationFormView.as_view(), login_url=SIGNUP_URL), name='registration'
    ),
    path('booking/', registration_required(views.BookingUpdateView.as_view()), name='booking'),
    path(
        'registration/success/',
        views.SuccessPageView.as_view(template_name='export_academy/registration_form_success.html'),
        name='registration-success',
    ),
    path(
        'booking/success/',
        views.SuccessPageView.as_view(template_name='export_academy/booking_success.html'),
        name='booking-success',
    ),
]
