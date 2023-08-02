from django.urls import path

from international_online_offer import views

app_name = 'international_online_offer'

urlpatterns = [
    path(
        '',
        views.Index.as_view(),
        name='index',
    ),
    path(
        'sector/',
        views.Sector.as_view(),
        name='sector',
    ),
    path(
        'intent/',
        views.Intent.as_view(),
        name='intent',
    ),
    path(
        'location/',
        views.Location.as_view(),
        name='location',
    ),
    path(
        'hiring/',
        views.Hiring.as_view(),
        name='hiring',
    ),
    path(
        'spend/',
        views.Spend.as_view(),
        name='spend',
    ),
    path(
        'profile/',
        views.Profile.as_view(),
        name='profile',
    ),
    path(
        'login/',
        views.Login.as_view(),
        name='login',
    ),
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup',
    ),
    path(
        'edit-your-answers/',
        views.EditYourAnswers.as_view(),
        name='edit-your-answers',
    ),
    path(
        'feedback/',
        views.Feedback.as_view(),
        name='feedback',
    ),
]
