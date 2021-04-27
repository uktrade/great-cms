from django.test import Client as TestClient
from django.urls import reverse_lazy
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceReturnedUnexpectedResult


class SearchSortBackend(BaseHealthCheckBackend):
    def check_status(self):
        # The order of results matters - this check ONLY confirms that Services are first
        # and Exopps are last but doesn't look to see whether Articles are above markets, or Articles are below Services
        #

        client = TestClient()
        response = client.get(reverse_lazy('search:search'), data={'q': 'qwerty123'}, follow=True)

        ordering_success = False
        if response.status_code == 200:
            results = response.context_data['results']
            # The 'type' below contains the user-facing/friendly-formatted version of
            # the type from  search.serializers._format_display_type()
            if (
                (len(results) == 6)
                and (results[0]['type'] == 'Service')  # noqa W503
                and (results[-1]['type'] == 'Export opportunity')  # noqa W503
            ):
                ordering_success = True

        if not ordering_success:
            raise ServiceReturnedUnexpectedResult('Search sort ordering via Activity Stream failed')

        return True
