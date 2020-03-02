from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView

from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

import sso.urls
import core.urls
import exportplan.urls


urlpatterns = [

    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtailadmin_urls)),
    path('documents/', include(wagtaildocs_urls)),
    path('sso/', include(sso.urls)),
    path('', include(core.urls, namespace="core")),
    path('export-plan/', include(exportplan.urls, namespace="exportplan")),

    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path('', include(wagtail_urls)),
]


if settings.ENFORCE_STAFF_SSO_ENABLED:
    urlpatterns += [
        path('admin/login/', RedirectView.as_view(url=reverse_lazy('authbroker_client:login'), query_string=True)),
        path('auth/', include('authbroker_client.urls')),
    ]


if settings.DEBUG:
    import debug_toolbar
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
