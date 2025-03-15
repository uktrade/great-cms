from django.contrib.auth.decorators import login_required
from django.urls import path, register_converter, reverse_lazy
from django.views.generic.base import RedirectView
from core.decorators import skip_ga360

from core.helpers import HashIdConverter
from exportplan import api, views

register_converter(HashIdConverter, 'hashid')

SIGNUP_URL = reverse_lazy('core:signup')
# NB our signup/signin redirection workflow following login_required
# relies on the value of REDIRECT_FIELD_NAME being the default: 'next'
# If you change the redirection parameter, other code will need
# updating too such as core.wagtail_hooks.authenticated_user_required,
# core.templatetags.url_tags.get_intended_destination and the loginUrl
# and signupUrl in base.html

app_name = 'exportplan'

urlpatterns = [
    # Temp redirect to old dashboard this can be removed over time this is to allow bookmarks and other services
    # To change the base dashboard link which is partially controlled by directory-constants
    path(
        'dashboard/',
        RedirectView.as_view(pattern_name='exportplan:index'),
        name='dashboard-redirect',
    ),
    path(
        '',
        views.ExportPlanIndex.as_view(),
        name='index',
    ),
    path(
        '<hashid:id>/',
        login_required(views.ExportPlanDashBoard.as_view(), login_url=SIGNUP_URL),
        name='dashboard',
    ),
    path(
        'start/',
        login_required(views.ExportPlanStart.as_view(), login_url=SIGNUP_URL),
        name='start',
    ),
    path(
        '<hashid:id>/update/',
        login_required(views.ExportPlanUpdate.as_view(), login_url=SIGNUP_URL),
        name='update',
    ),
    path(
        '<hashid:id>/marketing-approach/',
        login_required(views.ExportPlanMarketingApproachView.as_view(), login_url=SIGNUP_URL),
        name='marketing-approach',
    ),
    path(
        '<hashid:id>/adapting-your-product/',
        login_required(views.ExportPlanAdaptingYourProductView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'adapting-your-product'},
        name='adapting-your-product',
    ),
    path(
        '<hashid:id>/about-your-business/',
        login_required(views.ExportPlanAboutYourBusinessView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'about-your-business'},
        name='about-your-business',
    ),
    path(
        '<hashid:id>/target-markets-research/',
        login_required(views.ExportPlanTargetMarketsResearchView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'target-markets-research'},
        name='target-markets-research',
    ),
    path(
        '<hashid:id>/business-objectives/',
        login_required(views.ExportPlanBusinessObjectivesView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'business-objectives'},
        name='business-objectives',
    ),
    path(
        '<hashid:id>/costs-and-pricing/',
        login_required(views.CostsAndPricingView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'costs-and-pricing'},
        name='costs-and-pricing',
    ),
    path(
        '<hashid:id>/getting-paid/',
        login_required(views.GettingPaidView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'getting-paid'},
        name='getting-paid',
    ),
    path(
        '<hashid:id>/funding-and-credit/',
        login_required(views.FundingAndCreditView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'funding-and-credit'},
        name='funding-and-credit',
    ),
    path(
        '<hashid:id>/travel-plan/',
        login_required(views.TravelBusinessPoliciesView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'travel-plan'},
        name='travel-plan',
    ),
    path(
        '<hashid:id>/business-risk/',
        login_required(views.BusinessRiskView.as_view(), login_url=SIGNUP_URL),
        {'slug': 'business-risk'},
        name='business-risk',
    ),
    path('logo', login_required(views.LogoFormView.as_view(), login_url=SIGNUP_URL), name='add-logo'),
    path(
        'service-page/',
        login_required(views.ExportPlanServicePage.as_view(), login_url=SIGNUP_URL),
        name='service-page',
    ),
    path(
        r'<hashid:id>/pdf-download/',
        login_required(views.PDFDownload.as_view(), login_url=SIGNUP_URL),
        name='pdf-download',
    ),
    path(
        'api/export-plan/<hashid:id>/',
        skip_ga360(api.UpdateExportPlanAPIView.as_view()),
        name='api-update-export-plan',
    ),
    path(
        'api/target-age-country-population-data/<int:id>/',
        skip_ga360(api.TargetAgeCountryPopulationData.as_view()),
        name='api-target-age-groups',
    ),
    path(
        'api/society-data-by-country/',
        skip_ga360(api.ExportPlanSocietyDataByCountryView.as_view()),
        name='api-society-data-by-country',
    ),
    path(
        'api/calculate-cost-and-pricing/<int:id>/',
        skip_ga360(api.UpdateCalculateCostAndPricingAPIView.as_view()),
        name='api-calculate-cost-and-pricing',
    ),
    path(
        'api/model-object/manage/', skip_ga360(api.ModelObjectManageAPIView.as_view()), name='api-model-object-manage'
    ),
    path('api/create/', skip_ga360(api.CreateExportPlanAPIView.as_view()), name='api-export-plan-create'),
    path('api/delete/<hashid:id>/', skip_ga360(api.DeleteExportPlanAPIView.as_view()), name='api-export-plan-delete'),
]
