from django.utils.decorators import decorator_from_middleware
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from wagtail.core.models import Page

from activitystream.authentication import (
    ActivityStreamAuthentication,
    ActivityStreamHawkResponseMiddleware,
)
from activitystream.filters import PageFilter
from activitystream.serializers import PageSerializer
from domestic.models import ArticlePage, CountryGuidePage

MAX_PER_PAGE = 25


class ActivityStreamView(ListAPIView):
    """List-only view set for the activity stream"""

    authentication_classes = (ActivityStreamAuthentication,)
    permission_classes = ()

    @staticmethod
    def _build_after(request, after_ts, after_id):
        return request.build_absolute_uri(reverse('activity-stream')) + '?after={ts}_{id}'.format(
            ts=str(after_ts.timestamp()),
            id=str(after_id),
        )

    @decorator_from_middleware(ActivityStreamHawkResponseMiddleware)
    def list(self, request):
        """A single page of activities"""

        filter = PageFilter(
            request.GET,
            queryset=Page.objects.type(
                (
                    ArticlePage,
                    CountryGuidePage,
                )
            ).filter(live=True),
        )
        page_qs = filter.qs.specific().order_by('last_published_at', 'id')[:MAX_PER_PAGE]

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
