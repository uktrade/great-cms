from django.urls import path, reverse_lazy

from ioo import views

SIGNUP_URL = reverse_lazy('core:signup')
# NB our signup/signin redirection workflow following login_required
# relies on the value of REDIRECT_FIELD_NAME being the default: 'next'
# If you change the redirection parameter, other code will need
# updating too such as core.wagtail_hooks.authenticated_user_required,
# core.templatetags.url_tags.get_intended_destination and the loginUrl
# and signupUrl in base.html

app_name = 'ioo'

urlpatterns = [
    # Temp redirect to old dashboard this can be removed over time this is to allow bookmarks and other services
    # To change the base dashboard link which is partially controlled by directory-constants
    path(
        '',
        views.IOOIndex.as_view(),
        name='index',
    ),
]
