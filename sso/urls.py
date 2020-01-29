from django.urls import path

import sso.views

app_name = 'sso'


urlpatterns = [
    path(
        'api/business-login/',
        sso.views.SSOBusinessUserLoginView.as_view(),
        name='business-sso-login-api'
    ),
    path(
        'api/business-user-create/',
        sso.views.SSOBusinessUserCreateView.as_view(),
        name='business-sso-create-user-api'
    ),
]
