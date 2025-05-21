from unittest import mock

import pytest
from django.core.management import call_command

from domestic_growth.models import ExistingBusinessTriage, StartingABusinessTriage


@mock.patch(
    'domestic_growth.management.commands.move_triage_data_from_cache_to_db.cache.iter_keys',
    side_effect=[
        [':1:bgs:StartingABusinessTriage:1234', ':1:bgs:StartingABusinessTriage:5678'],
        [':1:bgs:ExistingBusinessTriage:1234', ':1:bgs:ExistingBusinessTriage:5678'],
    ],
    create=True,
)
@mock.patch(
    'domestic_growth.helpers.cache.get',
    side_effect=[
        {'triage_uuid': '1234', 'postcode': 'BT1A6K'},
        {'triage_uuid': '5678', 'sector_id': 'SL0003'},
        {'triage_uuid': '1234', 'postcode': 'BT1A6K'},
        {'triage_uuid': '5678', 'sector_id': 'SL0003'},
    ],
)
@pytest.mark.django_db
def test_move_cached_triage_data_to_db(mock_helper_cache, mock_command_cache):

    call_command('move_triage_data_from_cache_to_db')
    assert StartingABusinessTriage.objects.count() == 2

    assert StartingABusinessTriage.objects.get(triage_uuid='1234').postcode == 'BT1A6K'
    assert StartingABusinessTriage.objects.get(triage_uuid='5678').sector_id == 'SL0003'

    assert ExistingBusinessTriage.objects.count() == 2

    assert ExistingBusinessTriage.objects.get(triage_uuid='1234').postcode == 'BT1A6K'
    assert ExistingBusinessTriage.objects.get(triage_uuid='5678').sector_id == 'SL0003'


@mock.patch(
    'domestic_growth.management.commands.move_triage_data_from_cache_to_db.cache.iter_keys',
    return_value=[],
    create=True,
)
@mock.patch('domestic_growth.helpers.cache.get', return_value={})
@pytest.mark.django_db
def test_move_cached_triage_data_to_db_no_data(mock_helper_cache, mock_command_cache):
    call_command('move_triage_data_from_cache_to_db')
    assert StartingABusinessTriage.objects.count() == 0
    assert ExistingBusinessTriage.objects.count() == 0
