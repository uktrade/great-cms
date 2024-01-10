from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy

from international_online_offer import views

SIGNUP_URL = reverse_lazy('international_online_offer:login')

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
        login_required(views.ProfileView.as_view(), login_url=SIGNUP_URL),
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
        'change-your-answers/',
        views.EditYourAnswersView.as_view(),
        name='change-your-answers',
    ),
    path(
        'feedback/',
        views.FeedbackView.as_view(),
        name='feedback',
    ),
    path(
        'contact/',
        views.ContactView.as_view(),
        name='contact',
    ),
    path(
        'csat-widget-submit/',
        views.CsatWidgetView.as_view(),
        name='csat-widget-submit',
    ),
    path(
        'csat-feedback/',
        views.CsatFeedbackView.as_view(),
        name='csat-feedback',
    ),
    path(
        'trade-associations/',
        views.TradeAssociationsView.as_view(),
        name='trade-associations',
    ),
]
