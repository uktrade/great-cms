from unittest.mock import MagicMock, Mock

from international.templatetags.canonical_url_tags import get_canonical_url


def test_get_canonical_url(rf):
    request = Mock()
    request.scheme = 'https'
    request.path = '/international/expand-your-business-in-the-uk/'
    request.get_host = MagicMock(return_value='great.com')

    context_data = {'request': request}
    canonical_url = get_canonical_url(context_data)
    assert canonical_url == 'https://www.great.com/international/expand-your-business-in-the-uk/'
