from django.urls import path

from events import views

app_name = 'events'

urlpatterns = [
    path(
        'upcoming-events/',
        views.EventListView.as_view(),
        name='upcoming-events',
    ),
]
