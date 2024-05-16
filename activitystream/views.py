import django_filters.rest_framework
from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django.utils.decorators import decorator_from_middleware
from django.views.generic import TemplateView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from wagtail.models import Page

from activitystream.authentication import (
    ActivityStreamAuthentication,
    ActivityStreamHawkResponseMiddleware,
)
from activitystream.filters import (
    ActivityStreamCmsContentFilter,
    ActivityStreamExpandYourBusinessFilter,
    ActivityStreamExportAcademyFilter,
    PageFilter,
)
from activitystream.pagination import (
    ActivityStreamCmsContentPagination,
    ActivityStreamExpandYourBusinessPagination,
    ActivityStreamExportAcademyPagination,
)
from activitystream.serializers import (
    ActivityStreamCmsContentSerializer,
    ActivityStreamExpandYourBusinessCsatFeedbackDataSerializer,
    ActivityStreamExpandYourBusinessTriageDataSerializer,
    ActivityStreamExpandYourBusinessUserDataSerializer,
    ActivityStreamExportAcademyBookingSerializer,
    ActivityStreamExportAcademyCsatUserFeedbackDataSerializer,
    ActivityStreamExportAcademyEventSerializer,
    ActivityStreamExportAcademyRegistrationSerializer,
    ActivityStreamExportAcademyVideoOnDemandPageTrackingSerializer,
    PageSerializer,
)
from core.models import MicrositePage
from domestic.models import ArticlePage, CountryGuidePage
from export_academy.models import (
    Booking,
    CsatUserFeedback,
    Event,
    Registration,
    VideoOnDemandPageTracking,
)
from international_online_offer.models import CsatFeedback, TriageData, UserData


class ActivityStreamView(ListAPIView):
    """List-only view set to publish CMS content to the ActivityStream service"""

    MAX_PER_PAGE = 25

    authentication_classes = (ActivityStreamAuthentication,)
    permission_classes = ()
    filter_backends = [
        # This was a default project-wide setting in V1, but used selectively here to avoid
        # risking breaking other DRF usage
        django_filters.rest_framework.DjangoFilterBackend,
    ]

    @staticmethod
    def _build_after(request, after_ts, after_id):
        return request.build_absolute_uri(reverse('activitystream:articles')) + '?after={ts}_{id}'.format(
            ts=str(after_ts.timestamp()),
            id=str(after_id),
        )

    @decorator_from_middleware(ActivityStreamHawkResponseMiddleware)
    def list(self, request):
        """A single page of activities"""
        query_set1 = Page.objects.type((ArticlePage, CountryGuidePage)).filter(live=True)
        # locale_id = 1 just filters for english pages (atm we only want english pages in the search results)
        query_set2 = Page.objects.type((MicrositePage)).filter(live=True, locale_id=1)

        combined_query_set = query_set1 | query_set2

        filter = PageFilter(request.GET, queryset=combined_query_set)

        page_qs = filter.qs.specific().order_by('last_published_at', 'id')[: self.MAX_PER_PAGE]

        items = {
            '@context': 'https://www.w3.org/ns/activitystreams',
            'type': 'Collection',
            'orderedItems': PageSerializer(page_qs, many=True).data,
        }

        if not page_qs:
            next_page = {}
        else:
            last_article = page_qs[len(page_qs) - 1]
            next_page = {
                'next': self._build_after(
                    request,
                    last_article.last_published_at,
                    last_article.id,
                )
            }

        return Response(
            {
                **items,
                **next_page,
            }
        )


def key_pages_for_indexing(request):
    """Returns data on key pages (such as the Get Finance homepage) to
    include in search that are otherwise not provided via other APIs.

    Note that while the document structure is JSON, it's returned
    as text/html.

    This was called SearchKeyPagesView in Great V1, where it was not
    configurable with settings.BASE_URL
    """

    base_url = settings.BASE_URL
    if base_url[-1] == '/':
        base_url = base_url[:-1]

    return render(
        request=request,
        context={
            'base_url': base_url,
        },
        template_name='search-key-pages.json',
    )


class TestSearchAPIView(TemplateView):
    """This is a test-only version of the key_pages_for_indexing view.

    Due to shifts in the search order provided, we need to
    set up tests for the search order. The challenge is that
    all great-cms does is send an elasticsearch query to the elasticsearch
    database which sits inside the Activity Stream project. Therefore we
    can’t create fixtures in the DB. Also, if we mock the
    database response, then the test doesn’t test anything.

    Another approach would be to test against the staging or
    dev Elasticsearch database... but the results are not guaranteed to
    stay fixed as there are content changes to the data.

    The solution decided on is to feed into the dev database only
    a set of data with an obscure search term (i.e. all have the
    keyword “querty123”). The test runs a search for that query and
    tests the sort order of the results. Creating the test feed is
    done by creating a test API within Magna, which is this view.

    This is only consumed by the activitystream Dev environment,
    enabled via env config.

    (This was ported from V1 but collapsed from multiple classes into a single class)
    """

    template_name = 'test-search-api-pages.json'

    def dispatch(self, *args, **kwargs):
        # We only want to make this test view available in certain environments
        if not settings.FEATURE_FLAG_TEST_SEARCH_API_PAGES_ON:
            raise Http404()
        return super().dispatch(*args, **kwargs)


class ActivityStreamBaseView(ListAPIView):
    authentication_classes = (ActivityStreamAuthentication,)
    permission_classes = ()
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]

    @decorator_from_middleware(ActivityStreamHawkResponseMiddleware)
    def list(self, request, *args, **kwargs):
        """A single page of activities to be consumed by activity stream."""
        return super().list(request, *args, **kwargs)


class ActivityStreamExportAcademyBaseView(ActivityStreamBaseView):
    filterset_class = ActivityStreamExportAcademyFilter
    pagination_class = ActivityStreamExportAcademyPagination

    def get_queryset(self):
        return self.queryset.order_by('modified')


class ActivityStreamExpandYourBusinessBaseView(ActivityStreamBaseView):
    filterset_class = ActivityStreamExpandYourBusinessFilter
    pagination_class = ActivityStreamExpandYourBusinessPagination

    def get_queryset(self):
        return self.queryset.order_by('id')


class ActivityStreamExportAcademyEventView(ActivityStreamExportAcademyBaseView):
    queryset = Event.objects.all()
    serializer_class = ActivityStreamExportAcademyEventSerializer

    def get_queryset(self):
        return self.queryset.exclude(live__isnull=True).order_by('modified')


class ActivityStreamExportAcademyRegistrationView(ActivityStreamExportAcademyBaseView):
    queryset = Registration.objects.all()
    serializer_class = ActivityStreamExportAcademyRegistrationSerializer


class ActivityStreamExportAcademyBookingView(ActivityStreamExportAcademyBaseView):
    queryset = Booking.objects.all()
    serializer_class = ActivityStreamExportAcademyBookingSerializer


class ActivityStreamExpandYourBusinessUserDataView(ActivityStreamExpandYourBusinessBaseView):
    """View to list expand your business user data for the activity stream"""

    queryset = UserData.objects.all()
    serializer_class = ActivityStreamExpandYourBusinessUserDataSerializer


class ActivityStreamExpandYourBusinessTriageDataView(ActivityStreamExpandYourBusinessBaseView):
    """View to list expand your business triage data for the activity stream"""

    queryset = TriageData.objects.all()
    serializer_class = ActivityStreamExpandYourBusinessTriageDataSerializer


class ActivityStreamCmsContentView(ActivityStreamBaseView):
    """List view which live CMS content to the ActivityStream service"""

    serializer_class = ActivityStreamCmsContentSerializer
    filterset_class = ActivityStreamCmsContentFilter
    pagination_class = ActivityStreamCmsContentPagination
    queryset = Page.objects.exclude(
        Q(live=False) | Q(first_published_at__isnull=True) | Q(last_published_at__isnull=True)
    )

    def get_queryset(self):
        return self.queryset.order_by('id')


class ActivityStreamExpandYourBusinessCsatFeedbackDataView(ActivityStreamExpandYourBusinessBaseView):
    """View to list expand your business csat feedback data for the activity stream"""

    queryset = CsatFeedback.objects.all()
    serializer_class = ActivityStreamExpandYourBusinessCsatFeedbackDataSerializer


class ActivityStreamExportAcademyVideoOnDemandPageTrackingView(ActivityStreamExportAcademyBaseView):
    queryset = VideoOnDemandPageTracking.objects.all()
    serializer_class = ActivityStreamExportAcademyVideoOnDemandPageTrackingSerializer


class ActivityStreamExportAcademyBaseView(ActivityStreamBaseView):
    filterset_class = ActivityStreamExportAcademyFilter
    pagination_class = ActivityStreamExportAcademyPagination

    def get_queryset(self):
        return self.queryset.order_by('id')


class ActivityStreamExportAcademyCsatFeedbackDataView(ActivityStreamExportAcademyBaseView):
    """View to list export academy csat feedback data for the activity stream"""

    queryset = CsatUserFeedback.objects.all()
    serializer_class = ActivityStreamExportAcademyCsatUserFeedbackDataSerializer
