import json
from unittest.mock import Mock, patch

import pytest

from search.helpers import (
    format_query,
    parse_results,
    sanitise_page,
    search_with_activitystream,
)


@pytest.mark.parametrize(
    'param, expected',
    (
        (1, 1),
        (9999999999, 9999999999),
        (None, 1),
        ('one', 1),
        ('1', 1),
        ('2', 2),
        ('2a', 1),
    ),
)
def test_sanitise_page(param, expected):
    assert sanitise_page(param) == expected


@patch('search.helpers.sentry_sdk.capture_message')
def test_parse_results__unhappy_path(mock_capture_message):

    response = Mock()
    response.content = json.dumps({'error': 'test exception'})

    parse_results(response=response, query='', page=1)

    mock_capture_message.assert_called_once_with('There was an error in /search: test exception')


@patch('search.helpers.requests.Session.send')
def test_search_with_activitystream(mock_session_send):

    query = format_query(query='test query', page=1)

    search_with_activitystream(query)

    assert mock_session_send.call_count == 1
    issued_request = mock_session_send.call_args_list[0][0][0]

    for key, val in {
        'Content-Length': '666',
        'X-Forwarded-Proto': 'https',
        'X-Forwarded-For': 'debug',
        # 'Authorization': 'Hawk mac="8z+txQ3WIkigNHZbfCNLEFdFdOEa2y1fxELboX0Vgpg=", hash="1fsYlfW1YnvyKz7s1HJwjDVq3ys9o6ofYaWyAs6YHDI=", id="debug", ts="1579003201", nonce="o3TJ7i"',  # noqa
        'Content-Type': 'application/json',
    }.items():
        assert issued_request.headers[key] == val

    assert (
        'Authorization' in issued_request.headers
    )  #  tricky to test, even with freezegun, so this is just a smoke test
    assert issued_request.body and issued_request.body == query
