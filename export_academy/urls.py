from django.urls import path

from export_academy import views

app_name = 'export_academy'

urlpatterns = [
    path(
        'upcoming-events/',
        views.EventListView.as_view(),
        name='upcoming-events',
    ),
]
