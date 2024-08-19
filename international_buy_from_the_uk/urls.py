from django.urls import path

from international_buy_from_the_uk import views

app_name = 'international_buy_from_the_uk'

urlpatterns = [
    path(
        'contact/',
        views.ContactView.as_view(),
        name='contact',
    ),
]
