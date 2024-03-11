from decorator_include import decorator_include
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from great_components.decorators import skip_ga360
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail_transfer import urls as wagtailtransfer_urls

import activitystream.urls
import cms_extras.urls
import contact.urls
import core.urls
import domestic.urls
import export_academy.urls
import exportplan.urls
import international.urls
import international_online_offer.urls
import search.urls
import sso.urls
import sso_profile.urls

urlpatterns = []

if settings.ENFORCE_STAFF_SSO_ENABLED:
    urlpatterns += [
        path('admin/login/', RedirectView.as_view(url=reverse_lazy('authbroker_client:login'), query_string=True)),
        path('auth/', include('authbroker_client.urls')),
    ]


# WHEN ADDING TO THIS LIST CONSIDER WHETHER YOU SHOULD ALSO ADD ANY
# URL NAMES TO core.views.StaticViewSitemap
urlpatterns += [
    path('django-admin/', decorator_include(skip_ga360, admin.site.urls)),
    path(
        # Has to come before main /admin/ else will fail
        'admin/wagtail-transfer/',
        decorator_include(skip_ga360, wagtailtransfer_urls),
    ),
    path('admin/cms-extras/', decorator_include(skip_ga360, cms_extras.urls, namespace='cms_extras')),
    path('admin/', decorator_include(skip_ga360, wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),  # NB: doesn't skip GA as we may analytics on this
    path('great-cms-sso/', include(sso.urls)),
    path('search/', include(search.urls, namespace='search')),
    path('activity-stream/', include(activitystream.urls, namespace='activitystream')),
    path('export-plan/', include(exportplan.urls)),
    path('profile/', include(sso_profile.urls, namespace='sso_profile')),
    path('', include(domestic.urls, namespace='domestic')),
    path('', include(core.urls, namespace='core')),
    path('', include(contact.urls)),  # No prefix because not all of them start with /contact/
    path('export-academy/', include(export_academy.urls, namespace='export_academy')),
]

urlpatterns += [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path('', include(wagtail_urls)),
]


handler404 = 'core.views.handler404'

handler500 = 'core.views.handler500'

if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

urlpatterns = [path('international/', include(international.urls))] + urlpatterns

if settings.FEATURE_INTERNATIONAL_ONLINE_OFFER:
    urlpatterns = [
        path('international/expand-your-business-in-the-uk/', include(international_online_offer.urls))
    ] + urlpatterns

if settings.FEATURE_GREAT_CMS_OPENAPI_ENABLED:
    urlpatterns = [
        path('openapi/', SpectacularAPIView.as_view(), name='schema'),
        path(
            'openapi/ui/',
            login_required(SpectacularSwaggerView.as_view(url_name='schema'), login_url='admin:login'),
            name='swagger-ui',
        ),
        path(
            'openapi/ui/redoc/',
            login_required(SpectacularRedocView.as_view(url_name='schema'), login_url='admin:login'),
            name='redoc',
        ),
    ] + urlpatterns
