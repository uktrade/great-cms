import directory_healthcheck.views
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, re_path, reverse_lazy
from great_components.decorators import skip_ga360
from wagtail.contrib.sitemaps.views import sitemap as wagtail_sitemap

from config.url_redirects import redirects
from core import cms_slugs, views, views_api
from domestic.views.campaign import MicrositeView

app_name = 'core'

SIGNUP_URL = reverse_lazy('core:signup')
LOGIN_URL = reverse_lazy('core:login')
# NB our signup/signin redirection workflow following login_required
# relies on the value of REDIRECT_FIELD_NAME being the default: 'next'
# If you change the redirection parameter, other code will need
# updating too such as core.wagtail_hooks.authenticated_user_required,
# core.templatetags.url_tags.get_intended_destination and the loginUrl
# and signupUrl in base.html


def anonymous_user_required(function):
    inner = user_passes_test(
        lambda user: bool(user.is_anonymous),
        # redirect if the user DOES NOT pass the test
        cms_slugs.DASHBOARD_URL,
        None,
    )
    return inner(function)


available_sitemaps = {
    'cms-pages': views.CMSPagesSitemap,
    'static': views.StaticViewSitemap,
}


urlpatterns = [
    # WHEN ADDING TO THIS LIST CONSIDER WHETHER YOU SHOULD ALSO ADD THE URL NAME
    # TO core.views.StaticViewSitemap
    path(
        'sitemap.xml',
        skip_ga360(wagtail_sitemap),
        {'sitemaps': available_sitemaps},
        name='sitemap',
    ),
    path(
        'robots.txt',
        skip_ga360(views.RobotsView.as_view()),
        name='robots',
    ),
    path(
        'cookies/',
        skip_ga360(
            views.CookiePreferencesPageView.as_view(),
        ),
        name='cookie-preferences',
    ),
    path(
        'healthcheck/',
        skip_ga360(directory_healthcheck.views.HealthcheckView.as_view()),
        name='healthcheck',
    ),
    path(
        'healthcheck/ping/',
        skip_ga360(directory_healthcheck.views.PingView.as_view()),
        name='ping',
    ),
    path(
        'pingdom/ping.xml',
        skip_ga360(views.PingDomView.as_view()),
        name='pingdom',
    ),
    path('triage/<slug:step>/', skip_ga360(views.ServiceNoLongerAvailableView.as_view()), name='triage-wizard'),
    path('triage/', skip_ga360(views.ServiceNoLongerAvailableView.as_view()), name='triage-start'),
    path('custom/', skip_ga360(views.ServiceNoLongerAvailableView.as_view()), name='custom-page'),
    path(
        'where-to-export/',
        login_required(views.CompareCountriesView.as_view(), login_url=SIGNUP_URL),
        name='compare-countries',
    ),
    path(
        'capability/<str:topic>/<str:chapter>/<str:article>/',
        login_required(views.ArticleView.as_view(), login_url=SIGNUP_URL),
        name='capability-article',
    ),
    path('login/', anonymous_user_required(views.LoginView.as_view()), name='login'),
    path('logout/', login_required(skip_ga360(views.LogoutView.as_view())), name='logout'),
    path(
        'signup/',
        anonymous_user_required(
            skip_ga360(views.SignupView.as_view()),
        ),
        name='signup',
    ),
    path(
        'signup/company-name/',
        login_required(skip_ga360(views.CompanyNameFormView.as_view())),
        name='set-company-name',
    ),
    path(
        'signup/tailored-content/<str:step>/',
        anonymous_user_required(
            skip_ga360(views.SignupForTailoredContentWizardView.as_view(url_name='core:signup-wizard-tailored-content'))
        ),
        name='signup-wizard-tailored-content',
    ),
    path(
        'signup/export-plan/<str:step>/',
        login_required(
            skip_ga360(views.SignupForExportPlanWizardView.as_view(url_name='core:signup-wizard-export-plan'))
        ),
        name='signup-wizard-export-plan',
    ),
    path('contact-us/help/', skip_ga360(views.ContactUsHelpFormView.as_view()), name='contact-us-help'),
    path('contact-us/success/', skip_ga360(views.ContactUsHelpSuccessView.as_view()), name='contact-us-success'),
    path('api/update-company/', skip_ga360(views_api.UpdateCompanyAPIView.as_view()), name='api-update-company'),
    path('api/lookup-product/', skip_ga360(views_api.ProductLookupView.as_view()), name='api-lookup-product'),
    path(
        'api/lookup-product-schedule/',
        skip_ga360(views_api.ProductLookupScheduleView.as_view()),
        name='api-lookup-product-schedule',
    ),
    path('api/countries/', skip_ga360(views_api.CountriesView.as_view()), name='api-countries'),
    path(
        'api/suggested-countries/',
        skip_ga360(views_api.SuggestedCountriesView.as_view()),
        name='api-suggested-countries',
    ),
    path('api/create-token/', skip_ga360(views_api.CreateTokenView.as_view()), name='api-create-token'),
    path('api/check/', skip_ga360(views_api.CheckView.as_view()), name='api-check'),
    path('api/data-service/comtrade/', skip_ga360(views_api.ComTradeDataView.as_view()), name='api-comtrade-data'),
    path('api/data-service/countrydata/', skip_ga360(views_api.CountryDataView.as_view()), name='api-country-data'),
    path(
        'api/data-service/tradebarrier/',
        skip_ga360(views_api.TradeBarrierDataView.as_view()),
        name='api-trade-barrier-data',
    ),
    path(
        # THIS IS USED BY EXPORT PLAN / PERSONALISATION
        'api/companies-house/',
        skip_ga360(views_api.CompaniesHouseAPIView.as_view()),
        name='api-companies-house',
    ),
    path(
        'subtitles/<int:great_media_id>/<str:language>/content.vtt',
        login_required(
            # NB remove/update login_required() if we start serving subtitles for videos in
            # unauthed pages, but then ideally move to a UUID for the GreatMedia instance
            skip_ga360(views.serve_subtitles),
            login_url=LOGIN_URL,
        ),
        name='subtitles-serve',
    ),
    re_path(
        r'^microsites/.*/(?P<page_slug>[-a-zA-Z0-9_]+)/$',
        skip_ga360(MicrositeView.as_view()),
        name='microsites',
    ),
    re_path(
        r'^microsites/*(?P<page_slug>[-a-zA-Z0-9_]+)/$',
        skip_ga360(MicrositeView.as_view()),
        name='microsites',
    ),
    re_path(
        r'^campaign-site/.*/(?P<page_slug>[-a-zA-Z0-9_]+)/$',
        skip_ga360(MicrositeView.as_view()),
        name='campaign-site',
    ),
    re_path(
        r'^campaign-site/*(?P<page_slug>[-a-zA-Z0-9_]+)/$',
        skip_ga360(MicrositeView.as_view()),
        name='campaign-site',
    ),
    path('api/signed-url/', views.SignedURLView.as_view(), name='signed-url'),
    # WHEN ADDING TO THIS LIST CONSIDER WHETHER YOU SHOULD ALSO ADD THE URL NAME
    # TO core.views.StaticViewSitemap
]

if settings.FEATURE_DESIGN_SYSTEM:
    urlpatterns += [
        path(
            'design-system',
            skip_ga360(views.DesignSystemView.as_view()),
            name='design-system',
        ),
    ]

if settings.FEATURE_PRODUCT_MARKET_HERO and settings.FEATURE_PRODUCT_MARKET_SEARCH_ENABLED:
    urlpatterns += [
        path(
            'product-market',
            skip_ga360(views.ProductMarketView.as_view()),
            name='product-market',
        ),
    ]

if settings.FEATURE_GUIDED_JOURNEY:
    urlpatterns += [
        path(
            'your-export-guide/what-does-your-company-make-or-do',
            skip_ga360(views.GuidedJourneyStep1View.as_view()),
            name='guided-journey-step-1',
        ),
        path(
            'your-export-guide/what-does-your-company-make-or-do/edit',
            skip_ga360(views.GuidedJourneyStep1View.as_view()),
            {'edit': True, 'is_multi_step': True},
            name='guided-journey-step-1-edit',
        ),
        path(
            'your-export-guide/what-does-your-company-make-or-do/get',
            views.GuidedJourneyStep1GetView.as_view(),
            name='guided-journey-step-1-get',
        ),
        path(
            'your-export-guide/commodity-code-lookup',
            skip_ga360(views.GuidedJourneyStep2View.as_view()),
            name='guided-journey-step-2',
        ),
        path(
            'your-export-guide/commodity-code-lookup/edit',
            skip_ga360(views.GuidedJourneyStep2View.as_view()),
            {'edit': True},
            name='guided-journey-step-2-edit',
        ),
        path(
            'your-export-guide/target-export-market',
            skip_ga360(views.GuidedJourneyStep3View.as_view()),
            name='guided-journey-step-3',
        ),
        path(
            'your-export-guide/target-export-market/edit',
            skip_ga360(views.GuidedJourneyStep3View.as_view()),
            {'edit': True},
            name='guided-journey-step-3-edit',
        ),
        path(
            'your-export-guide/results',
            skip_ga360(views.GuidedJourneyStep4View.as_view()),
            name='guided-journey-step-4',
        ),
        path(
            'api/product-picker/<str:product>',
            skip_ga360(views_api.ProductPickerView.as_view()),
            name='api-product-picker',
        ),
    ]

if settings.FEATURE_BUSINESS_GROWTH_TRIAGE:
    urlpatterns += [
        path(
            'business-growth/tell-us-a-little-more',
            skip_ga360(views.BusinessGrowthTriageStep1View.as_view()),
            name='business-growth-triage-step-1',
        ),
        path(
            'business-growth/results',
            skip_ga360(views.BusinessGrowthTriageResultsView.as_view()),
            name='business-growth-triage-results',
        ),
    ]

urlpatterns += redirects
