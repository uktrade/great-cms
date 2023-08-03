from django.urls import path

from international_online_offer import views

app_name = 'international_online_offer'

urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index',
    ),
    path(
        'sector/',
        views.SectorView.as_view(),
        name='sector',
    ),
    path(
        'intent/',
        views.IntentView.as_view(),
        name='intent',
    ),
    path(
        'location/',
        views.LocationView.as_view(),
        name='location',
    ),
    path(
        'hiring/',
        views.HiringView.as_view(),
        name='hiring',
    ),
    path(
        'spend/',
        views.SpendView.as_view(),
        name='spend',
    ),
    path(
        'profile/',
        views.ProfileView.as_view(),
        name='profile',
    ),
    path(
        'login/',
        views.LoginView.as_view(),
        name='login',
    ),
    path(
        'signup/',
        views.SignUpView.as_view(),
        name='signup',
    ),
    path(
        'edit-your-answers/',
        views.EditYourAnswersView.as_view(),
        name='edit-your-answers',
    ),
    path(
        'feedback/',
        views.FeedbackView.as_view(),
        name='feedback',
    ),
]
