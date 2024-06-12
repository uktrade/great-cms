from directory_components.decorators import skip_ga360
from django.urls import path

from find_a_buyer import views

app_name = 'find_a_buyer'

urlpatterns = [
    # Seems to work
    path('verify/', views.CompanyVerifyView.as_view(), name='verify-company-hub'),

    # Seems to work
    path('verify/letter-send/', views.SendVerificationLetterView.as_view(), name='verify-company-address'),

    # Seems to work
    path(
        'verify/letter-confirm/', views.CompanyAddressVerificationView.as_view(), name='verify-company-address-confirm'
    ),

    # Needs testing
    path('verify/companies-house/', views.CompaniesHouseOauth2View.as_view(), name='verify-companies-house'),

    # Needs testing
    path(
        'companies-house-oauth2-callback/',
        views.CompaniesHouseOauth2CallbackView.as_view(),
        name='verify-companies-house-callback',
    ),

    # Needs testing
    path('data-science/buyers/', skip_ga360(views.BuyerCSVDumpView.as_view()), name='buyers-csv-dump'),

    # Needs testing
    path('data-science/suppliers/', skip_ga360(views.SupplierCSVDumpView.as_view()), name='suppliers-csv-dump'),
]
