from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, reverse_lazy

import core.views

app_name = 'core'

LOGIN_URL = reverse_lazy('core:login')


def anonymous_user_required(function):
    inner = user_passes_test(
        lambda user: bool(user.is_anonymous),
        reverse_lazy('core:dashboard'),
        None
    )
    return inner(function)


urlpatterns = [
    path(
        'dashboard/',
        login_required(core.views.DashboardView.as_view(), login_url=LOGIN_URL),
        name='dashboard'
    ),
    path(
        'markets/',
        core.views.MarketsView.as_view(),
        name='markets'
    ),
    path(
        'capability/<str:topic>/<str:chapter>/<str:article>/',
        login_required(core.views.ArticleView.as_view(), login_url=LOGIN_URL),
        name='capability-article'
    ),
    path(
        'login/',
        anonymous_user_required(core.views.LoginView.as_view()),
        name='login'
    ),
    path(
        'signup/',
        anonymous_user_required(core.views.SignupView.as_view()),
        name='signup'
    ),
    path(
        'api/update-company/',
        core.views.UpdateCompanyAPIView.as_view(),
        name='api-update-company'
    ),
    path(
        'api/lookup-product/',
        core.views.ProductLookupView.as_view(),
        name='api-lookup-product'
    ),
]
