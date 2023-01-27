from django.contrib.auth.decorators import login_required
from django.urls import path

from core.urls import SIGNUP_URL
from export_academy import views

app_name = 'export_academy'

urlpatterns = [
    path(
        'upcoming-events/',
        views.EventListView.as_view(),
        name='upcoming-events',
    ),
    path(
        'registration/', login_required(views.RegistrationFormView.as_view(), login_url=SIGNUP_URL), name='registration'
    ),
    path(
        'registration-success/',
        views.RegistrationSuccessPageView.as_view(),
        name='registration-success',
    ),
    path(
        'booking-success/',
        views.BookingSuccessPageView.as_view(),
        name='booking-success',
    ),
]
