from unittest import mock
from learn import helpers


@mock.patch.object(helpers, 'get_popular_export_destinations')
def test_get_suggested_countries(mock_get_popular_export_destinations):
    mock_get_popular_export_destinations.return_value = [('China', 16), ('France', 12)]
    actual = helpers.get_suggested_countries('Aerospace')

    assert actual == [{'value': 'CN', 'label': 'China'}, {'value': 'FR', 'label': 'France'}]
    assert mock_get_popular_export_destinations.call_count == 1
    assert mock_get_popular_export_destinations.call_args == mock.call('Aerospace')
