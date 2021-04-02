from django.urls import path
from great_components.decorators import skip_ga360

import search.views

urlpatterns = [
    path(
        r'key-pages/',
        skip_ga360(search.views.SearchKeyPagesView.as_view()),
        name='search-key-pages',
    )
]
