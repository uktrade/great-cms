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
        login_required(views.SectorView.as_view(), login_url=SIGNUP_URL),
        name='sector',
    ),
    path(
        'intent/',
        login_required(views.IntentView.as_view(), login_url=SIGNUP_URL),
        name='intent',
    ),
    path(
        'location/',
        login_required(views.LocationView.as_view(), login_url=SIGNUP_URL),
        name='location',
    ),
    path(
        'hiring/',
        login_required(views.HiringView.as_view(), login_url=SIGNUP_URL),
        name='hiring',
    ),
    path(
        'spend/',
        login_required(views.SpendView.as_view(), login_url=SIGNUP_URL),
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
        login_required(views.EditYourAnswersView.as_view(), login_url=SIGNUP_URL),
        name='change-your-answers',
    ),
    path(
        'feedback/',
        views.FeedbackView.as_view(),
        name='feedback',
    ),
    path(
        'csat-widget-submit/',
        login_required(views.CsatWidgetView.as_view(), login_url=SIGNUP_URL),
        name='csat-widget-submit',
    ),
    path(
        'csat-feedback/',
        login_required(views.CsatFeedbackView.as_view(), login_url=SIGNUP_URL),
        name='csat-feedback',
    ),
    path(
        'trade-associations/',
        login_required(views.TradeAssociationsView.as_view(), login_url=SIGNUP_URL),
        name='trade-associations',
    ),
    path(
        'business-cluster-information/',
        login_required(views.BusinessClusterView.as_view(), login_url=SIGNUP_URL),
        name='bci',
    ),
]
