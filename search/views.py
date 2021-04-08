import logging

from django.views.generic import TemplateView
from requests.exceptions import RequestException

from search import helpers

logger = logging.getLogger(__name__)


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
