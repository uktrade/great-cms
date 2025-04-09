from django.urls import path
from great_components.decorators import skip_ga360

from search.views import (
    OpensearchView,
    SearchFeedbackFormView,
    SearchFeedbackSuccessView,
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

# Search URL
# Serve search through Opensearch
urlpatterns += [
    path(
        '',
        skip_ga360(OpensearchView.as_view()),
        name='search',
    ),
]
