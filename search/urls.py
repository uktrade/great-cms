from django.conf import settings
from django.urls import path
from great_components.decorators import skip_ga360

from search.views import (
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

# Serve search page linked to gov-pass
if settings.OPENSEARCH_PROVIDER == 'govuk-paas':
    urlpatterns += [
        path(
            '',
            skip_ga360(SearchView.as_view()),
            name='search',
        )
    ]
# Serve search page linked to AWS Opensearch
elif settings.OPENSEARCH_PROVIDER in ['localhost', 'aws']:
    urlpatterns += [
        path(
            '',
            skip_ga360(OpensearchView.as_view()),
            name='search',
        )
    ]
