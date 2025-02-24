import requests
from django.core.management import BaseCommand
from rest_framework import status

from international_online_offer.models import TradeAssociation


class Command(BaseCommand):
    """
    Checks the URLs of Trade Associations to ensure that they do not resolve to a 404 page not found response code.
    Trade Associations that do not have a valid link will not be displayed to the end user.
    """

    help = 'Checks the URLs of Trade Associations to ensure they are live'

    def check_page_found(self, url: str, verb: str = 'HEAD') -> bool:
        headers = {'User-Agent': 'requests/2.32.3'}

        try:
            response = requests.request(verb, url, headers=headers, allow_redirects=True, timeout=10)
        except requests.exceptions.MissingSchema:
            response = requests.request(verb, f'https://{url}', headers=headers, allow_redirects=True, timeout=10)
        except requests.exceptions.SSLError:
            # when calling a page programmatically sometimes an SSL error occurs even when the browser version is ok
            response = requests.request(verb, url, headers=headers, allow_redirects=True, timeout=10, verify=False)
        except Exception:
            return False

        if response.status_code == status.HTTP_404_NOT_FOUND and verb == 'HEAD':
            # some webservers are configured not to accept a HEAD request. Try GET.
            return self.check_page_found(url, verb='GET')

        return response.status_code != status.HTTP_404_NOT_FOUND

    def handle(self, *args, **options):
        for trade_association in TradeAssociation.objects.all():
            try:
                link_valid = self.check_page_found(trade_association.website_link)
            except Exception:
                link_valid = False

            if trade_association.link_valid != link_valid:
                trade_association.link_valid = link_valid
                trade_association.save()
