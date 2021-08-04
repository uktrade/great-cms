from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from great_components.decorators import skip_ga360

from exportplan import api, views

SIGNUP_URL = reverse_lazy('core:signup')
# NB our signup/signin redirection workflow following login_required
# relies on the value of REDIRECT_FIELD_NAME being the default: 'next'
# If you change the redirection parameter, other code will need
# updating too such as core.wagtail_hooks.authenticated_user_required,
# core.templatetags.url_tags.get_intended_destination and the loginUrl
# and signupUrl in base.html

app_name = 'exportplan'

urlpatterns = [
    path(
        '',
        views.ExportPlanIndex.as_view(),
        name='index',
    ),
    path(
        'start/',
        login_required(views.ExportPlanStart.as_view(), login_url=SIGNUP_URL),
        name='start',
    ),
    path(
        'section/marketing-approach/',
        login_required(views.ExportPlanMarketingApproachView.as_view(), login_url=SIGNUP_URL),
        name='marketing-approach',
    ),
    path(
        'section/adapting-your-product/',
        login_required(views.ExportPlanAdaptingYourProductView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'adapting-your-product'},
        name='adapting-your-product',
    ),
    path(
        'section/about-your-business/',
        login_required(views.ExportPlanAboutYourBusinessView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'about-your-business'},
        name='about-your-business',
    ),
    path(
        'section/target-markets-research/',
        login_required(views.ExportPlanTargetMarketsResearchView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'target-markets-research'},
        name='target-markets-research',
    ),
    path(
        'section/business-objectives/',
        login_required(views.ExportPlanBusinessObjectivesView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'business-objectives'},
        name='business-objectives',
    ),
    path(
        'section/costs-and-pricing/',
        login_required(views.CostsAndPricingView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'costs-and-pricing'},
        name='costs-and-pricing',
    ),
    path(
        'section/getting-paid/',
        login_required(views.GettingPaidView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'getting-paid'},
        name='getting-paid',
    ),
    path(
        'section/funding-and-credit/',
        login_required(views.FundingAndCreditView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'funding-and-credit'},
        name='funding-and-credit',
    ),
    path(
        'section/travel-plan/',
        login_required(views.TravelBusinessPoliciesView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'travel-plan'},
        name='travel-plan',
    ),
    path(
        'section/business-risk/',
        login_required(views.BusinessRiskView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'business-risk'},
        name='business-risk',
    ),
    path(
        'section/<slug:slug>/',
        login_required(views.ExportPlanSectionView.as_view(), login_url=SIGNUP_URL),
        name='section',
    ),
    path('logo', login_required(views.LogoFormView.as_view(), login_url=SIGNUP_URL), name='add-logo'),
    path(
        'service-page/',
        login_required(views.ExportPlanServicePage.as_view(), login_url=SIGNUP_URL),
        name='service-page',
    ),
    path(
        'list/',
        login_required(views.ExportPlanList.as_view(), login_url=SIGNUP_URL),
        name='list',
    ),
    path('pdf-download/', login_required(views.PDFDownload.as_view(), login_url=SIGNUP_URL), name='pdf-download'),
    path('api/export-plan/', skip_ga360(api.UpdateExportPlanAPIView.as_view()), name='api-update-export-plan'),
    path(
        'api/population-data-by-country/',
        skip_ga360(api.ExportPlanPopulationDataByCountryView.as_view()),
        name='api-population-data-by-country',
    ),
    path(
        'api/target-age-country-population-data/',
        skip_ga360(api.TargetAgeCountryPopulationData.as_view()),
        name='api-target-age-groups',
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
    path(
        'api/model-object/manage/', skip_ga360(api.ModelObjectManageAPIView.as_view()), name='api-model-object-manage'
    ),
]
