from django.urls import path
from core.decorators import skip_ga360

from sso.api import (
    LessonCompletedAPIView,
    QuestionnaireAPIView,
    UserDataAPIView,
    UserProfileAPIView,
)
from sso.views import (
    SSOBusinessUserCreateView,
    SSOBusinessUserLoginView,
    SSOBusinessUserLogoutView,
    SSOBusinessVerifyCodeView,
)

app_name = 'sso'


urlpatterns = [
    path('api/business-login/', skip_ga360(SSOBusinessUserLoginView.as_view()), name='business-sso-login-api'),
    path('api/business-logout/', skip_ga360(SSOBusinessUserLogoutView.as_view()), name='business-sso-logout-api'),
    path(
        'api/business-user-create/',
        skip_ga360(SSOBusinessUserCreateView.as_view()),
        name='business-sso-create-user-api',
    ),
    path(
        'api/business-verify-code/',
        skip_ga360(SSOBusinessVerifyCodeView.as_view()),
        name='business-sso-verify-code-api',
    ),
    path(
        'api/v1/lesson-completed/<int:lesson>/', skip_ga360(LessonCompletedAPIView.as_view()), name='lesson-completed'
    ),
    path(
        'api/v1/user-profile/',
        skip_ga360(UserProfileAPIView.as_view()),
        name='user-profile-api',
    ),
    path('api/v1/user-questionnaire/', skip_ga360(QuestionnaireAPIView.as_view()), name='user-questionnaire-api'),
    path('api/v1/user-data/<str:name>/', skip_ga360(UserDataAPIView.as_view()), name='user-data-api'),
]
