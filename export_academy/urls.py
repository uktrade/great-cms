from django.urls import path

from export_academy import views

app_name = 'export_academy'


urlpatterns = [
    path(
        '',
        views.LandingPageView.as_view(),
        name='index',
    ),
    path(
        'upcoming-events/',
        views.EventListView.as_view(),
        name='upcoming-events',
    ),
]
