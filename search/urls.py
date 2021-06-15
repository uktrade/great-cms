from django.urls import path
from great_components.decorators import skip_ga360

import search.views

app_name = 'search'

# WHEN ADDING TO THIS LIST CONSIDER WHETHER YOU SHOULD ALSO ADD THE URL NAME
# TO core.views.StaticViewSitemap

urlpatterns = [
    path(
        '',
        skip_ga360(search.views.SearchView.as_view()),
        name='search',
    ),
    path(
        'feedback/',
        search.views.SearchFeedbackFormView.as_view(),
        name='feedback',
    ),
]
