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
<<<<<<< HEAD
=======
        'guide/',
        views.IOOGuide.as_view(),
        name='guide',
    ),
    path(
>>>>>>> a7fbc4d30 (Feature/ioo 428 detailed guide (#2034))
        'contact/',
        views.IOOContact.as_view(),
        name='contact',
    ),
    path(
<<<<<<< HEAD
        'login/',
        views.IOOLogin.as_view(),
        name='login',
    ),
    path(
        'signup/',
        views.IOOSignUp.as_view(),
        name='signup',
=======
        'guide/<str:success>/',
        views.IOOGuide.as_view(),
        name='contact-success',
>>>>>>> a7fbc4d30 (Feature/ioo 428 detailed guide (#2034))
    ),
]
