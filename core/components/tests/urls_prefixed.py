from django.conf.urls import url, include

import tests.urls


urlpatterns = [
    url(
        r'^components/',
        include(tests.urls.urlpatterns)
    )
]
