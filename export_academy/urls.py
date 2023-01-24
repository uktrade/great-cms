from django.urls import path

from export_academy import views

app_name = 'export_academy'

urlpatterns = [
    path(
        'export-academy/',
        views.EventListView.as_view(),
        name='upcoming-events',
    ),
]
