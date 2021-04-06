import logging

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.views.generic import TemplateView
from requests.exceptions import RequestException

from search import helpers

logger = logging.getLogger(__name__)


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
    all GDUI does is send an elasticsearch query to the elasticsearch
    database which sits inside the Activity Stream project. Therefore we
    can’t create fixtures in the DB. Also, f we mock the
    database response, then the test doesn’t test anything.

    Another approach would be to test against the staging or
    dev Elasticsearch database... but the results are not guaranteed to
    stay fixed as there are content changes to the data.

    The solution decided on is to feed into the dev database only
    a set of data with an obscure search term (i.e. all have the
    keyword “query123”). The test runs a search for that query and
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


class SearchView(TemplateView):
    """Search results page.

    URL parameters:
        q:string - string to be searched
        page:int - results page number
    """

    template_name = 'search.html'
    page_type = 'SearchResultsPage'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)

        results = {}
        query = self.request.GET.get('q', '')
        submitted = self.request.GET.get('submitted', '')
        page = helpers.sanitise_page(self.request.GET.get('page', '1'))

        common = {
            'submitted': submitted,
            'query': query,
            'current_page': page,
        }

        try:
            elasticsearch_query = helpers.format_query(query, page)
            response = helpers.search_with_activitystream(elasticsearch_query)
        except RequestException:
            logger.error(
                "Activity Stream connection for Search failed. Query: '{query}'".format(
                    query=query,
                )
            )
            results = {
                'error_status_code': 500,
                'error_message': 'Activity Stream connection failed',
            }
        else:
            if response.status_code != 200:
                results = {
                    'error_message': response.content,
                    'error_status_code': response.status_code,
                }

            else:
                results = helpers.parse_results(
                    response,
                    query,
                    page,
                )

        return {**context, **common, **results}
