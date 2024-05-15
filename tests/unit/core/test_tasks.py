import datetime
from unittest import mock

import pytest

from core.tasks import enact_page_schedule, update_geoip_data
from tests.unit.core.factories import MicrositeFactory, MicrositePageFactory


@pytest.mark.skip(reason='Temp Disabled')
@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.retrieve_file')
@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.decompress')
def test_update_geoip_data_success(mock_decompress, mock_retrieve_file):
    update_geoip_data()

    assert mock_decompress.call_count == 2

    assert mock_retrieve_file.call_count == 2

    assert mock_retrieve_file.call_args_list == [
        mock.call(
            edition_id='GeoLite2-City',
        ),
        mock.call(
            edition_id='GeoLite2-Country',
        ),
    ]


@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.retrieve_file')
@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.decompress')
def test_update_geoip_data_failure(mock_decompress, mock_retrieve_file):
    mock_decompress.side_effect = ValueError()

    with pytest.raises(ValueError):
        update_geoip_data()


@pytest.mark.django_db
def test_enact_page_scheduled(rf, user, domestic_homepage):
    request = rf.get('/')
    request.user = user
    now = datetime.datetime.now()

    microsite = MicrositeFactory(
        title='Microsite',
        parent=domestic_homepage,
    )

    microsite_page_with_expire_date = MicrositePageFactory(
        slug='microsite-page-with-expire-date',
        title='Test',
        page_title='Test',
        parent=microsite,
        expire_at=now,
    )

    assert microsite_page_with_expire_date.live is True

    enact_page_schedule()
    microsite_page_with_expire_date.refresh_from_db()

    assert microsite_page_with_expire_date.live is False
