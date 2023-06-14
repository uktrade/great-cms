from django.urls import path
from great_components.decorators import skip_ga360

import activitystream.views

app_name = 'activitystream'

urlpatterns = [
    path(
        r'key-pages/',
        skip_ga360(activitystream.views.key_pages_for_indexing),
        name='search-key-pages',
    ),
    path(
        'test-api/',
        skip_ga360(activitystream.views.TestSearchAPIView.as_view()),
        name='search-test-api',
    ),
    path(
        'v1/',  # v1 refers to OUR version of the endpoint we're making available
        skip_ga360(activitystream.views.ActivityStreamView.as_view()),
        name='cms-content',
    ),
    path(
        'ukea-events/',
        skip_ga360(activitystream.views.ExportAcademyEventActivityStreamView.as_view()),
        name='ukea-events',
    ),
    path(
        'ukea-registrations/',
        skip_ga360(activitystream.views.ExportAcademyRegistrationActivityStreamView.as_view()),
        name='ukea-registrations',
    ),
    path(
        'ukea-bookings/',
        skip_ga360(activitystream.views.ExportAcademyBookingActivityStreamView.as_view()),
        name='ukea-bookings',
    ),
    path(
        'eyb-triages/',
        skip_ga360(activitystream.views.ActivityStreamExpandYourBusinessTriageDataViewSet.as_view()),
        name='eyb-triages',
    ),
    path(
        'eyb-users/',
        skip_ga360(activitystream.views.ActivityStreamExpandYourBusinessUserDataViewSet.as_view()),
        name='eyb-users',
    ),
]
