from django.urls import path, reverse_lazy
from django.contrib.auth.decorators import login_required

from exportplan import views, ajax

LOGIN_URL = reverse_lazy('core:login')

app_name = 'exportplan'

urlpatterns = [
    path('section/marketing-approach/', views.ExportPlanMarketingApproachView.as_view(), name='marketing-approach'),
    path('logo', views.LogoFormView.as_view(), name='add-logo'),
    path(
        'section/target-markets/',
        login_required(views.ExportPlanTargetMarketsView.as_view(), login_url=LOGIN_URL),
        {'slug': 'target-markets'},
        name='target-markets'
    ),
    path(
        'section/brand-and-product/',
        login_required(views.ExportPlanBrandAndProductView.as_view(), login_url=LOGIN_URL),
        {'slug': 'brand-and-product'},
        name='brand-and-product'
    ),
    path(
        'section/objectives/',
        login_required(views.ExportPlanBusinessObjectivesView.as_view(), login_url=LOGIN_URL),
        {'slug': 'objectives'},
        name='objectives'
    ),
    path(
        'section/<slug:slug>/',
        login_required(views.ExportPlanSectionView.as_view(), login_url=LOGIN_URL),
        name='section'
    ),
    path(
        'logo',
        login_required(views.LogoFormView.as_view(), login_url=LOGIN_URL),
        name='add-logo'
    ),
    path(
        'api/recommended-countries/',
        login_required(ajax.ExportPlanRecommendedCountriesDataView.as_view(), login_url=LOGIN_URL),
        name='ajax-recommended-countries-data'
    ),
    path('api/export-plan/', views.UpdateExportPlanAPIView.as_view(), name='api-update-export-plan'),
    path('api/remove-country-data/', ajax.ExportPlanRemoveCountryDataView.as_view(), name='ajax-remove-country-data'),
    path('api/country-data/', ajax.ExportPlanCountryDataView.as_view(), name='ajax-country-data'),
]
