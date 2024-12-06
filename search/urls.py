from django.conf import settings
from django.urls import path
from great_components.decorators import skip_ga360

from search.views import (
    OpensearchAdminView,
    OpensearchView,
    SearchFeedbackFormView,
    SearchFeedbackSuccessView,
    SearchView,
)

app_name = 'search'

# WHEN ADDING TO THIS LIST CONSIDER WHETHER YOU SHOULD ALSO ADD THE URL NAME
# TO core.views.StaticViewSitemap

urlpatterns = [
    path(
        'feedback/',
        SearchFeedbackFormView.as_view(),
        name='feedback',
    ),
    path('feedback/success', SearchFeedbackSuccessView.as_view(), name='feedback-success'),
]

# Search URLs
# How do we power our search? # TODO: Remove flag when new search is released
if settings.FEATURE_OPENSEARCH:  # Serve search through Opensearch
    urlpatterns += [
        path(
            '',
            skip_ga360(OpensearchView.as_view()),
            name='search',
        ),
    ]
else:  # Serve legacy search that queries ActivityStream
    urlpatterns += [
        path(
            '',
            skip_ga360(SearchView.as_view()),
            name='search',
        ),
    ]

# Display the latest WIP search preview? # TODO: Remove when new search is released
if settings.FEATURE_OPENSEARCH and settings.FEATURE_SEARCH_PREVIEW:
    urlpatterns += [
        path(
            'preview/',
            skip_ga360(OpensearchAdminView.as_view()),
            name='preview',
        ),
    ]
