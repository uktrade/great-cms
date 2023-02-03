from django.urls import path

from international_online_offer import views

app_name = 'international_online_offer'

urlpatterns = [
    path(
        '',
        views.IOOIndex.as_view(),
        name='index',
    ),
]
