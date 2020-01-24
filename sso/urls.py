from django.conf.urls import url

import sso.views

app_name = 'sso'


urlpatterns = [
    url(
    	r'^api/business-login/$',
    	sso.views.SSOBusinessUserLoginView.as_view(),
    	name='business-login-api'
    ),
]
