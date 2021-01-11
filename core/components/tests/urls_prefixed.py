from django.conf.urls import include, url

import tests.urls

urlpatterns = [url(r'^components/', include(tests.urls.urlpatterns))]
