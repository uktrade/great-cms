from unittest import mock

from core.tasks import update_geoip_data


@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.retrieve_file')
@mock.patch('core.management.commands.download_geolocation_data.GeolocationRemoteFileArchive.decompress')
def test_update_geoip_data_success(mock_decompress, mock_retrieve_file):

    update_geoip_data()

    assert mock_decompress.call_count == 2

    # assert mock_decompress.call_args_list == [
    #     mock.call(
    #         file_like_object=MagicMock(name='retrieve_file()',  id='5414645088'),
    #         file_name=settings.GEOIP_CITY,
    #     ),
    #     mock.call(
    #         file_like_object=MagicMock(name='retrieve_file()', id='5414645088'),
    #         file_name=settings.GEOIP_COUNTRY,
    #     ),
    # ]

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
    update_geoip_data()
