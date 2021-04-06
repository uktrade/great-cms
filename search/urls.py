from django.urls import path
from great_components.decorators import skip_ga360

import search.views

urlpatterns = [
    path(
        r'key-pages/',
        skip_ga360(search.views.key_pages_for_indexing),
        name='search-key-pages',
    )
]
