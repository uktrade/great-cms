from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, reverse_lazy
from great_components.decorators import skip_ga360

import core.views

app_name = 'core'

LOGIN_URL = reverse_lazy('core:login')


def anonymous_user_required(function):
    inner = user_passes_test(
        lambda user: bool(user.is_anonymous),
        reverse_lazy('core:login'),
        None
    )
    return inner(function)


urlpatterns = [
    path(
        'markets/',
        skip_ga360(core.views.MarketsView.as_view()),
        name='markets'
    ),
    path(
        'capability/<str:topic>/<str:chapter>/<str:article>/',
        login_required(skip_ga360(core.views.ArticleView.as_view()), login_url=LOGIN_URL),
        name='capability-article'
    ),
    path(
        'login/',
        anonymous_user_required(skip_ga360(core.views.LoginView.as_view())),
        name='login'
    ),
    path(
        'signup/',
        anonymous_user_required(skip_ga360(core.views.SignupView.as_view())),
        name='signup'
    ),
    path(
        'signup/company-name/',
        login_required(skip_ga360(core.views.CompanyNameFormView.as_view())),
        name='set-company-name'
    ),
    path(
        'signup/tailored-content/<str:step>/',
        anonymous_user_required(
            skip_ga360(
                core.views.SignupForTailoredContentWizardView.as_view(url_name='core:signup-wizard-tailored-content'))
        ),
        name='signup-wizard-tailored-content'
    ),
    path(
        'signup/export-plan/<str:step>/',
        anonymous_user_required(
            skip_ga360(core.views.SignupForExportPlanWizardView.as_view(url_name='core:signup-wizard-export-plan'))
        ),
        name='signup-wizard-export-plan'
    ),
    path(
        'api/update-company/',
        skip_ga360(core.views.UpdateCompanyAPIView.as_view()),
        name='api-update-company'
    ),
    path(
        'api/lookup-product/',
        skip_ga360(core.views.ProductLookupView.as_view()),
        name='api-lookup-product'
    ),
    path(
        'api/create-token/',
        skip_ga360(core.views.CreateTokenView.as_view()),
        name='api-create-token'
    )
]
