from django.urls import path

from find_a_buyer import views

app_name = 'find_a_buyer'

urlpatterns = [

    path(
        'verify/companies-house/',
        views.CompaniesHouseOauth2View.as_view(),
        name='verify-companies-house'
    ),

    path(
        'verify/letter-send/',
        views.SendVerificationLetterView.as_view(),
        name='verify-company-address'
    ),

    path(
        'verify/letter-confirm/',
        views.CompanyAddressVerificationView.as_view(),
        name='verify-company-address-confirm'
    ),

    path(
        'verify/',
        views.CompanyVerifyView.as_view(),
        name='verify-company-hub'
    ),

]