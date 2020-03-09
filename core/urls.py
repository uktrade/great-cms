from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, reverse_lazy

import core.views

app_name = 'core'


def anonymous_user_required(function):
    inner = user_passes_test(
        lambda user: bool(user.is_anonymous),
        reverse_lazy('core:dashboard'),
        None
    )
    return inner(function)


urlpatterns = [
    path(
        '',
        anonymous_user_required(core.views.LandingPageView.as_view()),
        name='landing-page'
    ),
    path(
        'dashboard/',
        login_required(core.views.DashboardView.as_view(), login_url='/'),
        name='dashboard'
    ),
    path(
        'capability/<str:topic>/<str:chapter>/<str:article>/',
        login_required(core.views.ArticleView.as_view(), login_url='/'),
        name='capability-article'
    ),
    path(
        'login/',
        anonymous_user_required(core.views.LoginView.as_view()),
        name='login'
    ),
    path(
        'api/create-company/',
        core.views.EnrolCompanyAPIView.as_view(),
        name='api-create-company'
    ),
    path(
        'api/update-company/',
        core.views.UpdateCompanyAPIView.as_view(),
        name='api-update-company'
    ),
]
