from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin

from core.helpers import is_bgs_domain


class CheckForBGSDomainMiddleware(MiddlewareMixin):

    def process_request(self, request):
        absolute_uri = request.build_absolute_uri()
        parts = absolute_uri.split('/')
        stripped_parts = parts[:3] + [part for part in parts[3:] if part.strip()]
        url = f"/{'/'.join(stripped_parts[3:])}"
        if is_bgs_domain(request) and f'/{settings.GREAT_INTERNATIONAL_URL}' in url:
            bgs_international_url = url.replace(
                f'/{settings.GREAT_INTERNATIONAL_URL}', f'/{settings.BGS_INTERNATIONAL_URL}'
            )
            return redirect(bgs_international_url)
