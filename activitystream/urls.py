from django.urls import path
from core.decorators import skip_ga360

import activitystream.views

app_name = 'activitystream'

urlpatterns = [
    path(
        r'key-pages/',
        skip_ga360(activitystream.views.key_pages_for_indexing),
        name='search-key-pages',
    ),
    path(
        r'cms-content/',
        skip_ga360(activitystream.views.ActivityStreamCmsContentView.as_view()),
        name='cms-content',
    ),
    path(
        'test-api/',
        skip_ga360(activitystream.views.TestSearchAPIView.as_view()),
        name='search-test-api',
    ),
    path(
        'v1/',  # v1 refers to OUR version of the endpoint we're making available
        skip_ga360(activitystream.views.ActivityStreamView.as_view()),
        name='articles',
    ),
    path(
        'ukea-events/',
        skip_ga360(activitystream.views.ActivityStreamExportAcademyEventView.as_view()),
        name='ukea-events',
    ),
    path(
        'ukea-registrations/',
        skip_ga360(activitystream.views.ActivityStreamExportAcademyRegistrationView.as_view()),
        name='ukea-registrations',
    ),
    path(
        'ukea-bookings/',
        skip_ga360(activitystream.views.ActivityStreamExportAcademyBookingView.as_view()),
        name='ukea-bookings',
    ),
    path(
        'eyb-triages/',
        skip_ga360(activitystream.views.ActivityStreamExpandYourBusinessTriageDataView.as_view()),
        name='eyb-triages',
    ),
    path(
        'eyb-users/',
        skip_ga360(activitystream.views.ActivityStreamExpandYourBusinessUserDataView.as_view()),
        name='eyb-users',
    ),
    path(
        'ukea-videoondemandpagetracking/',
        skip_ga360(activitystream.views.ActivityStreamExportAcademyVideoOnDemandPageTrackingView.as_view()),
        name='ukea-videoondemandpagetracking',
    ),
    path(
        'domestic-hcsats/',
        skip_ga360(activitystream.views.ActivityStreamDomesticHCSATFeedbackDataView.as_view()),
        name='domestic-hcsats',
    ),
]
