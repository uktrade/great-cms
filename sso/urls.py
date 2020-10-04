from django.urls import path
from great_components.decorators import skip_ga360

from sso.views import (SSOBusinessUserLoginView,
                       SSOBusinessUserLogoutView,
                       SSOBusinessUserCreateView,
                       SSOBusinessVerifyCodeView)
from sso.api import LessonCompletedAPIView

app_name = 'sso'


urlpatterns = [
    path(
        'api/business-login/',
        skip_ga360(SSOBusinessUserLoginView.as_view()),
        name='business-sso-login-api'
    ),
    path(
        'api/business-logout/',
        skip_ga360(SSOBusinessUserLogoutView.as_view()),
        name='business-sso-logout-api'
    ),
    path(
        'api/business-user-create/',
        skip_ga360(SSOBusinessUserCreateView.as_view()),
        name='business-sso-create-user-api'
    ),
    path(
        'api/business-verify-code/',
        skip_ga360(SSOBusinessVerifyCodeView.as_view()),
        name='business-sso-verify-code-api'
    ),
    path(
        'api/v1/lesson-completed/<int:lesson>/',
        skip_ga360(LessonCompletedAPIView.as_view()),
        name='lesson-completed'
    )
]
