import http
import urllib.parse as urlparse

import requests
from django.conf import settings


def get_exops_data(hashed_sso_id):
    response = exopps_client.get_exops_data(hashed_sso_id)
    if response.status_code == http.client.FORBIDDEN:
        return None
    elif response.status_code == http.client.OK:
        return response.json()
    raise response.raise_for_status()


class ExportingIsGreatClient:
    auth = requests.auth.HTTPBasicAuth(
        settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME,
        settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD,
    )
    base_url = settings.EXPORTING_OPPORTUNITIES_API_BASE_URL
    endpoints = {'exops_data': 'export-opportunities/api/profile_dashboard'}
    secret = settings.EXPORTING_OPPORTUNITIES_API_SECRET

    def get(self, partial_url, params):
        params['shared_secret'] = self.secret
        url = urlparse.urljoin(self.base_url, partial_url)
        return requests.get(url, params=params, auth=self.auth)

    def get_exops_data(self, hashed_sso_id):
        params = {'sso_user_id': hashed_sso_id}
        return self.get(self.endpoints['exops_data'], params)


exopps_client = ExportingIsGreatClient()
