from django.urls import path

from exportplan import views, ajax

app_name = 'exportplan'

urlpatterns = [
    path('start/', views.ExportPlanStartView.as_view(), name='start'),
    path('create/', views.ExportPlanCreateView.as_view(), name='create'),
    path('section/target-markets/', views.ExportPlanTargetMarketsView.as_view(), name='target-markets'),
    path('section/<slug:slug>/', views.ExportPlanSectionView.as_view(), name='section'),
    path(
        'api/recommended-countries/',
        ajax.ExportPlanRecommendedCountriesDataView.as_view(),
        name='ajax-recommended-countries-data'
    ),
    path('api/country-data/', ajax.ExportPlanCountryDataView.as_view(), name='ajax-country-data')
]
