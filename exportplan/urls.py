from django.urls import path

from exportplan import views, ajax

app_name = 'exportplan'

urlpatterns = [
    path('section/target-markets/', views.ExportPlanTargetMarketsView.as_view(), name='target-markets'),
    path('section/<slug:slug>/', views.ExportPlanSectionView.as_view(), name='section'),
    path(
        'api/recommended-countries/',
        ajax.ExportPlanRecommendedCountriesDataView.as_view(),
        name='ajax-recommended-countries-data'
    ),
    path('api/export-plan/', views.UpdateExportPlanAPIView.as_view(), name='api-update-export-plan'),
    path('api/country-data/', ajax.ExportPlanCountryDataView.as_view(), name='ajax-country-data'),
]
