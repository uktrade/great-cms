from django.urls import path

from international import views

app_name = 'international'

urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index',
    ),
]
