from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy

from international_online_offer import views

SIGNUP_URL = reverse_lazy('international_online_offer:login')

app_name = 'international_online_offer'

urlpatterns = [
    path(
        'tell-us-about-your-business/',
        login_required(views.AboutYourBusinessView.as_view(), login_url=SIGNUP_URL),
        name='about-your-business',
    ),
    path(
        'business-headquarters/',
        login_required(views.BusinessHeadQuartersView.as_view(), login_url=SIGNUP_URL),
        name='business-headquarters',
    ),
    path(
        'find-your-company/',
        login_required(views.FindYourCompanyView.as_view(), login_url=SIGNUP_URL),
        name='find-your-company',
    ),
    path(
        'company-details/',
        login_required(views.CompanyDetailsView.as_view(), login_url=SIGNUP_URL),
        name='company-details',
    ),
    path(
        'business-sector/',
        login_required(views.BusinessSectorView.as_view(), login_url=SIGNUP_URL),
        name='business-sector',
    ),
    path(
        'when-do-you-want-to-set-up/',
        login_required(views.WhenDoYouWantToSetupView.as_view(), login_url=SIGNUP_URL),
        name='when-want-setup',
    ),
    path(
        'do-you-know-your-set-up-location/',
        login_required(views.KnowSetupLocationView.as_view(), login_url=SIGNUP_URL),
        name='know-setup-location',
    ),
    path(
        'contact-details/',
        login_required(views.ContactDetailsView.as_view(), login_url=SIGNUP_URL),
        name='contact-details',
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
    path('dnb-typeahead-company-lookup/', views.DNBTypeaheadView.as_view(), name='dnb-typeahead-company-lookup'),
    path('dnb-company-search/', views.DNBCompanySearchView.as_view(), name='dnb-company-search'),
]
