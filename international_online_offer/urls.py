from django.urls import path

from international_online_offer import views

app_name = 'international_online_offer'

urlpatterns = [
    path(
        '',
        views.ExpandYourBusinessIndex.as_view(),
        name='index',
    ),
    path(
        'sector/',
        views.ExpandYourBusinessSector.as_view(),
        name='sector',
    ),
    path(
        'intent/',
        views.ExpandYourBusinessIntent.as_view(),
        name='intent',
    ),
    path(
        'location/',
        views.ExpandYourBusinessLocation.as_view(),
        name='location',
    ),
    path(
        'hiring/',
        views.ExpandYourBusinessHiring.as_view(),
        name='hiring',
    ),
    path(
        'spend/',
        views.ExpandYourBusinessSpend.as_view(),
        name='spend',
    ),
    path(
        'profile/',
        views.ExpandYourBusinessProfile.as_view(),
        name='profile',
    ),
    path(
        'login/',
        views.ExpandYourBusinessLogin.as_view(),
        name='login',
    ),
    path(
        'signup/',
        views.ExpandYourBusinessSignUp.as_view(),
        name='signup',
    ),
    path(
        'edit-your-answers/',
        views.ExpandYourBusinessEditYourAnswers.as_view(),
        name='edit-your-answers',
    ),
    path(
        'feedback/',
        views.ExpandYourBusinessFeedback.as_view(),
        name='feedback',
    ),
]
