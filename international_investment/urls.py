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
]
