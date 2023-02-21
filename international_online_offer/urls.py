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
    path('sector/submit', views.IOOSector.as_view(), name="sector-submit"),
]
