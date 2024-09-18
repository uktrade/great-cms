import logging

from mohawk.exc import HawkFail
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from activitystream.helpers import authorise

logger = logging.getLogger(__name__)
NO_CREDENTIALS_MESSAGE = 'Authentication credentials were not provided.'
INCORRECT_CREDENTIALS_MESSAGE = 'Incorrect authentication credentials.'


class ActivityStreamAuthentication(BaseAuthentication):
    def authenticate_header(self, request):
        """This is returned as the WWW-Authenticate header when
        AuthenticationFailed is raised. DRF also requires this
        to send a 401 (as opposed to 403)
        """
        return 'Hawk'

    def authenticate(self, request):
        """Authenticates a request using Hawk signature

        If either of these suggest we cannot authenticate, AuthenticationFailed
        is raised, as required in the DRF authentication flow
        """

        return self.authenticate_by_hawk(request)

    def authenticate_by_hawk(self, request):
        logger.info(f'HTTP Headers {request.META}')
        if 'HTTP_AUTHORIZATION' not in request.META:
            raise AuthenticationFailed(NO_CREDENTIALS_MESSAGE)

        # Required to make mohawk auth work locally, and no harm in production,
        # so saves having to have it as a temporary monkey-patch
        request.META['CONTENT_TYPE'] = b''

        try:
            hawk_receiver = authorise(request)
        except HawkFail as e:
            logger.warning('Failed authentication {e}'.format(e=e))
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

        return (None, hawk_receiver)


class ActivityStreamHawkResponseMiddleware:
    """Adds the Server-Authorization header to the response, so the originator
    of the request can authenticate the response
    """

    def __init__(self, *args, **kwargs):
        pass

    def process_response(self, viewset, response):
        response['Server-Authorization'] = viewset.request.auth.respond(
            content=response.content,
            content_type=response['Content-Type'],
        )
        return response
