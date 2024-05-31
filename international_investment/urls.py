from django.urls import path

from international_investment import views

app_name = 'international_investment'

urlpatterns = [
    path(
        '',
        views.IndexView.as_view(),
        name='index',
    ),
    path(
        'investment-fund/',
        views.InvestmentFundView.as_view(),
        name='investment-fund',
    ),
    path(
        'investment-types/',
        views.InvestmentTypesView.as_view(),
        name='investment-types',
    ),
    path(
        'investment-estimate/',
        views.InvestmentEstimateView.as_view(),
        name='investment-estimate',
    ),
    path(
        'investment-contact-details/',
        views.InvestmentContactView.as_view(),
        name='investment-contact-details',
    ),
    path(
        'investment-submission-success/',
        views.InvestmentSubmissionSuccessView.as_view(),
        name='investment-submission-success',
    ),
]
