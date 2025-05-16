from django.http import HttpResponsePermanentRedirect
from django.utils.deprecation import MiddlewareMixin

from core.helpers import is_bgs_domain


class CheckForBGSDomainMiddleware(MiddlewareMixin):

    bgs_redirect_mapping = {
        'campaign-site': 'campaign',
        'markets': 'export-from-uk/market-guides',
        'campaigns': 'export-from-uk/guidance',
        'report-a-trade-barrier': 'export-from-uk/resources/report-a-trade-barrier',
        'get-finance': 'export-from-uk/resources/uk-export-finance',
        'find-a-buyer': 'export-from-uk/resources/find-a-buyer',
        'services': 'export-from-uk/resources',
        'international': 'invest-in-uk',
    }

    def process_request(self, request):
        absolute_uri = request.build_absolute_uri()
        absolute_uri_parts = absolute_uri.split('/')
        url = f"/{'/'.join(absolute_uri_parts[3:])}"
        if is_bgs_domain(request):
            if absolute_uri_parts[3] in self.bgs_redirect_mapping.keys():
                mapping_key = absolute_uri_parts[3]
                redirect_url = url.replace(mapping_key, self.bgs_redirect_mapping[mapping_key])
                return HttpResponsePermanentRedirect(redirect_url)
