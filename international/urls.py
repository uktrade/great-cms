from django.urls import path

from international import views

app_name = 'international'

urlpatterns = [
    path(
        'site-help/',
        views.ContactView.as_view(),
        name='contact',
    ),
    path(
        'site-help/success/',
        views.ContactSuccessView.as_view(),
        name='contact-success',
    ),
]
