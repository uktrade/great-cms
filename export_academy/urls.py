from django.contrib.auth.decorators import login_required
from django.urls import path

from core.urls import SIGNUP_URL
from export_academy import views
from export_academy.helpers import check_registration

app_name = 'export_academy'


urlpatterns = [
    path(
        'upcoming-events/',
        views.EventListView.as_view(),
        name='upcoming-events',
    ),
    path(
        'registration/<uuid:booking_id>',
        login_required(views.RegistrationFormView.as_view(), login_url=SIGNUP_URL),
        name='registration',
    ),
    path('booking/', check_registration(views.BookingUpdateView.as_view()), name='booking'),
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
