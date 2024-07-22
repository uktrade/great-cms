import directory_healthcheck.views
from directory_components.decorators import skip_ga360
from django.conf.urls import include
from django.urls import path, re_path

from find_a_buyer import views

app_name = 'find_a_buyer'

healthcheck_urls = [
    re_path(r'^$', skip_ga360(directory_healthcheck.views.HealthcheckView.as_view()), name='healthcheck'),
]

urlpatterns = [
    path('healthcheck/', include((healthcheck_urls, 'healthcheck'), namespace='healthcheck')),
    path('verify/', views.CompanyVerifyView.as_view(), name='verify-company-hub'),
    path('verify/letter-send/', views.SendVerificationLetterView.as_view(), name='verify-company-address'),
    path(
        'verify/letter-confirm/', views.CompanyAddressVerificationView.as_view(), name='verify-company-address-confirm'
    ),
    path('verify/companies-house/', views.CompaniesHouseOauth2View.as_view(), name='verify-companies-house'),
    path(
        'companies-house-oauth2-callback/',
        views.CompaniesHouseOauth2CallbackView.as_view(),
        name='verify-companies-house-callback',
    ),
    path('data-science/buyers/', skip_ga360(views.BuyerCSVDumpView.as_view()), name='buyers-csv-dump'),
    path('data-science/suppliers/', skip_ga360(views.SupplierCSVDumpView.as_view()), name='suppliers-csv-dump'),
]
