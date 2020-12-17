from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, reverse_lazy
from great_components.decorators import skip_ga360

from core import cms_slugs, views, views_api

app_name = 'core'

LOGIN_URL = reverse_lazy('core:login')


def anonymous_user_required(function):
    inner = user_passes_test(
        lambda user: bool(user.is_anonymous),
        # redirect if the user DOES NOT pass the test
        cms_slugs.DASHBOARD_URL,
        None,
    )
    return inner(function)


urlpatterns = [
    path('markets/', views.MarketsView.as_view(), name='markets'),
    path(
        'compare-countries/',
        login_required(views.CompareCountriesView.as_view(), login_url=LOGIN_URL),
        name='compare-countries',
    ),
    path(
        'capability/<str:topic>/<str:chapter>/<str:article>/',
        login_required(views.ArticleView.as_view(), login_url=LOGIN_URL),
        name='capability-article',
    ),
    path('login/', anonymous_user_required(views.LoginView.as_view()), name='login'),
    path('signup/', anonymous_user_required(views.SignupView.as_view()), name='signup'),
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
    path('api/countries/', skip_ga360(views_api.CountriesView.as_view()), name='api-countries'),
    path(
        'api/suggested-countries/',
        skip_ga360(views_api.SuggestedCountriesView.as_view()),
        name='api-suggested-countries',
    ),
    path('api/create-token/', skip_ga360(views_api.CreateTokenView.as_view()), name='api-create-token'),
    path('api/check/', skip_ga360(views_api.CheckView.as_view()), name='api-check'),
    path('api/data-service/comtrade/', skip_ga360(views_api.ComTradeDataView.as_view()), name='api-comtrade-data'),
]
