from django.urls import path

from exportplan import views, ajax

app_name = 'exportplan'

urlpatterns = [
    path(
        'section/target-markets/',
        views.ExportPlanTargetMarketsView.as_view(),
        {'slug': 'target-markets'},
        name='target-markets'
    ),
    path(
        'section/brand-and-product/',
        views.ExportPlanBrandAndProductView.as_view(),
        {'slug': 'brand-and-product'},
        name='brand-and-product'
    ),
    path('section/<slug:slug>/', views.ExportPlanSectionView.as_view(), name='section'),
    path('logo', views.LogoFormView.as_view(), name='add-logo'),
    path(
        'api/recommended-countries/',
        ajax.ExportPlanRecommendedCountriesDataView.as_view(),
        name='ajax-recommended-countries-data'
    ),
    path('api/export-plan/', views.UpdateExportPlanAPIView.as_view(), name='api-update-export-plan'),
    path('api/remove-country-data/', ajax.ExportPlanRemoveCountryDataView.as_view(), name='ajax-remove-country-data'),
    path('api/country-data/', ajax.ExportPlanCountryDataView.as_view(), name='ajax-country-data'),
]
