from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from great_components.decorators import skip_ga360

from exportplan import api, views

LOGIN_URL = reverse_lazy('core:login')

app_name = 'exportplan'

urlpatterns = [
    path(
        'section/marketing-approach/',
        login_required(views.ExportPlanMarketingApproachView.as_view(), login_url=LOGIN_URL),
        name='marketing-approach',
    ),
    path(
        'section/adaptation-for-your-target-market/',
        login_required(views.ExportPlanAdaptationForTargetMarketView.as_view(), login_url=LOGIN_URL),
        {'slug': 'adaptation-for-your-target-market'},
        name='adaptation-for-your-target-market',
    ),
    path(
        'section/about-your-business/',
        login_required(views.ExportPlanAboutYourBusinessView.as_view(), login_url=LOGIN_URL),
        {'slug': 'about-your-business'},
        name='about-your-business',
    ),
    path(
        'section/target-markets-research/',
        login_required(views.ExportPlanTargetMarketsResearchView.as_view(), login_url=LOGIN_URL),
        {'slug': 'target-markets-research'},
        name='target-markets-research',
    ),
    path(
        'section/business-objectives/',
        login_required(views.ExportPlanBusinessObjectivesView.as_view(), login_url=LOGIN_URL),
        {'slug': 'business-objectives'},
        name='business-objectives',
    ),
    path(
        'section/costs-and-pricing/',
        login_required(views.CostsAndPricingView.as_view(), login_url=LOGIN_URL),
        {'slug': 'costs-and-pricing'},
        name='costs-and-pricing',
    ),
    path(
        'section/funding-and-credit/',
        login_required(views.FundingAndCreditView.as_view(), login_url=LOGIN_URL),
        {'slug': 'funding-and-credit'},
        name='funding-and-credit',
    ),
    path(
        'section/<slug:slug>/',
        login_required(views.ExportPlanSectionView.as_view(), login_url=LOGIN_URL),
        name='section',
    ),
    path('logo', login_required(views.LogoFormView.as_view(), login_url=LOGIN_URL), name='add-logo'),
    path(
        'service-page/', login_required(views.ExportPlanServicePage.as_view(), login_url=LOGIN_URL), name='service-page'
    ),
    path(
        'api/recommended-countries/',
        login_required(skip_ga360(api.ExportPlanRecommendedCountriesDataView.as_view()), login_url=LOGIN_URL),
        name='ajax-recommended-countries-data',
    ),
    path('api/export-plan/', skip_ga360(api.UpdateExportPlanAPIView.as_view()), name='api-update-export-plan'),
    path(
        'api/remove-country-data/',
        skip_ga360(api.ExportPlanRemoveCountryDataView.as_view()),
        name='api-remove-country-data',
    ),
    path('api/remove-sector/', skip_ga360(api.ExportPlanRemoveSectorView.as_view()), name='api-remove-sector'),
    path('api/country-data/', skip_ga360(api.ExportPlanCountryDataView.as_view()), name='api-country-data'),
    path(
        'api/population-data-by-country/',
        skip_ga360(api.ExportPlanPopulationDataByCountryView.as_view()),
        name='api-population-data-by-country',
    ),
    path(
        'api/target-age-country-population-data/',
        skip_ga360(api.TargetAgeCountryPopulationData.as_view()),
        name='api-target-age-country-population-data',
    ),
    path(
        'api/society-data-by-country/',
        skip_ga360(api.ExportPlanSocietyDataByCountryView.as_view()),
        name='api-society-data-by-country',
    ),
    path(
        'api/calculate-cost-and-pricing/',
        skip_ga360(api.UpdateCalculateCostAndPricingAPIView.as_view()),
        name='api-calculate-cost-and-pricing',
    ),
    path('api/objectives/create/', skip_ga360(api.ObjectivesCreateAPIView.as_view()), name='api-objectives-create'),
    path('api/objectives/update/', skip_ga360(api.ObjectivesUpdateAPIView.as_view()), name='api-objectives-update'),
    path('api/objectives/delete/', skip_ga360(api.ObjectivesDestroyAPIView.as_view()), name='api-objectives-delete'),
    path(
        'api/route-to-markets/create/',
        skip_ga360(api.RouteToMarketsCreateAPIView.as_view()),
        name='api-route-to-markets-create',
    ),
    path(
        'api/route-to-markets/update/',
        skip_ga360(api.RouteToMarketsUpdateAPIView.as_view()),
        name='api-route-to-markets-update',
    ),
    path(
        'api/route-to-markets/delete/',
        skip_ga360(api.RouteToMarketsDestroyAPIView.as_view()),
        name='api-route-to-markets-delete',
    ),
    path(
        'api/target-markets-documents/create/',
        skip_ga360(api.TargetMarketDocumentsCreateAPIView.as_view()),
        name='api-target-markets-documents-create',
    ),
    path(
        'api/target-markets-documents/update/',
        skip_ga360(api.TargetMarketDocumentUpdateAPIView.as_view()),
        name='api-target-markets-documents-update',
    ),
    path(
        'api/target-markets-documents/delete/',
        skip_ga360(api.TargetMarketDocumentsDestroyAPIView.as_view()),
        name='api-target-markets-documents-delete',
    ),
    path(
        'api/funding-credit-options/create/',
        skip_ga360(api.FundingCreditOptionsCreateAPIView.as_view()),
        name='api-funding-credit-options-create',
    ),
    path(
        'api/funding-credit-options/update/',
        skip_ga360(api.FundingCreditOptionsUpdateAPIView.as_view()),
        name='api-funding-credit-options-update',
    ),
    path(
        'api/funding-credit-options/delete/',
        skip_ga360(api.FundingCreditOptionsDestroyAPIView.as_view()),
        name='api-funding-credit-options-delete',
    ),
]
