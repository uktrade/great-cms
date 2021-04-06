from django.urls import path
from great_components.decorators import skip_ga360

import search.views

app_name = 'search'

urlpatterns = [
    path(
        r'key-pages/',
        skip_ga360(search.views.key_pages_for_indexing),
        name='search-key-pages',
    ),
    path(
        'test-api/',
        skip_ga360(search.views.TestSearchAPIView.as_view()),
        name='search-test-api',
    ),
    path(
        '',
        search.views.SearchView.as_view(),
        name='search',
    ),
]
