from django.urls import path

from international_online_offer import views

app_name = 'international_online_offer'

urlpatterns = [
    path(
        '',
        views.IOOIndex.as_view(),
        name='index',
    ),
    path(
        'sector/',
        views.IOOSector.as_view(),
        name='sector',
    ),
    path(
        'intent/',
        views.IOOIntent.as_view(),
        name='intent',
    ),
    path(
        'location/',
        views.IOOLocation.as_view(),
        name='location',
    ),
    path(
        'hiring/',
        views.IOOHiring.as_view(),
        name='hiring',
    ),
    path(
        'spend/',
        views.IOOSpend.as_view(),
        name='spend',
    ),
    path(
        'guide/',
        views.IOOGuide.as_view(),
        name='guide',
    ),
    path(
        'contact/',
        views.IOOContact.as_view(),
        name='contact',
    ),
    path(
        'guide/<str:success>/',
        views.IOOGuide.as_view(),
        name='contact-success',
    ),
]
