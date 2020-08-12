from django.urls import path
from great_components.decorators import skip_ga360

import sso.views

app_name = 'sso'


urlpatterns = [
    path(
        'api/business-login/',
        skip_ga360(sso.views.SSOBusinessUserLoginView.as_view()),
        name='business-sso-login-api'
    ),
    path(
        'api/business-user-create/',
        skip_ga360(sso.views.SSOBusinessUserCreateView.as_view()),
        name='business-sso-create-user-api'
    ),
    path(
        'api/business-verify-code/',
        skip_ga360(sso.views.SSOBusinessVerifyCodeView.as_view()),
        name='business-sso-verify-code-api'
    ),
    path(
        'api/v1/lesson-completed/<int:lesson>/',
        skip_ga360(sso.views.LessonCompletedAPIView.as_view()),
        name='lesson-completed'
    )
]
