from unittest.mock import MagicMock, Mock

from international.templatetags.int_canonical_url_tags import (
    get_canonical_url,
    get_hreflang_tags,
)


def test_get_canonical_url(rf):
    request = Mock()
    request.scheme = 'https'
    request.path = '/international/expand-your-business-in-the-uk/'
    request.get_host = MagicMock(return_value='great.com')

    context_data = {'request': request}
    canonical_url = get_canonical_url(context_data)
    assert canonical_url == 'https://www.great.com/international/expand-your-business-in-the-uk/'


def test_get_hreflang_url_without(rf):
    request = Mock()
    request.scheme = 'https'
    request.path = '/international/expand-your-business-in-the-uk/'
    request.get_host = MagicMock(return_value='great.com')
    request.get_full_path = MagicMock(return_value='/international/expand-your-business-in-the-uk/?q=test')

    context_data = {'request': request}
    hreflang_tags = get_hreflang_tags(context_data)
    assert hreflang_tags == ''


def test_get_hreflang_url_with(rf):
    request = Mock()
    request.scheme = 'https'
    request.path = '/international/expand-your-business-in-the-uk/'
    request.get_host = MagicMock(return_value='great.com')
    request.get_full_path = MagicMock(return_value='/international/expand-your-business-in-the-uk/')

    context_data = {'request': request}
    hreflang_tags = get_hreflang_tags(context_data)
    assert (
        hreflang_tags
        == '<link rel="alternate" hreflang="en" href="https://www.great.com/international/expand-your-business-in-the-uk/" />'  # noqa E501
        '\n<link rel="alternate" hreflang="x-default" href="https://www.great.com/international/expand-your-business-in-the-uk/" />'  # noqa E501
    )
