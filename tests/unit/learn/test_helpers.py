from unittest import mock

from learn import helpers


@mock.patch.object(helpers, 'get_popular_export_destinations')
def test_get_suggested_countries_for_sector(mock_get_popular_export_destinations):
    mock_get_popular_export_destinations.return_value = [('China', 16), ('France', 12)]
    actual = helpers.get_suggested_countries_for_sector('Aerospace')

    assert actual == [{'value': 'CN', 'label': 'China'}, {'value': 'FR', 'label': 'France'}]
    assert mock_get_popular_export_destinations.call_count == 1
    assert mock_get_popular_export_destinations.call_args == mock.call('Aerospace')


def test_get_suggested_countries_for_user(rf, user, mock_get_company_profile):
    request = rf.get('/')
    request.user = user
    mock_get_company_profile.return_value = {'expertise_industries': ['SL10003']}

    actual = helpers.get_suggested_countries_for_user(request)

    assert actual == [
        {'value': 'UA', 'label': 'Ukraine'},
        {'value': 'IN', 'label': 'India'},
        {'value': 'AU', 'label': 'Australia'},
        {'value': 'DE', 'label': 'Germany'},
    ]
