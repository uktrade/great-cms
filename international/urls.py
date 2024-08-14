from django.urls import path

from international import views

app_name = 'international'

urlpatterns = [
    path(
        'contact/',
        views.ContactView.as_view(),
        name='contact',
    )
]
