from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from core.helpers import is_bgs_domain


class CheckForBGSDomainMiddleware(MiddlewareMixin):

    def process_request(self, request):
        absolute_uri = request.build_absolute_uri()
        if is_bgs_domain(request) and f'/{settings.GREAT_INTERNATIONAL_URL}/' in absolute_uri:
            bgs_international_url = absolute_uri.replace(
                f'/{settings.GREAT_INTERNATIONAL_URL}/', f'/{settings.BGS_INTERNATIONAL_URL}/'
            )
            return redirect(bgs_international_url)
