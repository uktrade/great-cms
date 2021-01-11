from django.conf.urls import include, url
from django.views import View
from django.views.generic.base import RedirectView

import directory_components.views
import demo.views


admin_urls = [
    url(
        r"^thing/$",
        RedirectView.as_view(url='/login/'),
        name='thing'
    ),
]

urlpatterns = [
    url(
        r'^$',
        View.as_view(),
        name='index',
    ),
    url(r'^admin/', include(admin_urls)),
    url(
        r"^robots\.txt$",
        directory_components.views.RobotsView.as_view(),
        name='robots'
    ),
    url(
        r'^404/$',
        demo.views.Trigger404View.as_view(),
        name='404',
    ),
    url(
        r'^500/$',
        demo.views.Trigger500ErrorView.as_view(),
        name='500',
    ),
    url(
        r"^sitemap\.txt$",
        View.as_view(),
        name='sitemap'
    ),
    url(
        r"^some/path/$",
        View.as_view(),
        name='some-path'
    ),
    url(r'^i18n/', include('django.conf.urls.i18n')),
]

handler404 = 'directory_components.views.handler404'

handler500 = 'directory_components.views.handler500'
