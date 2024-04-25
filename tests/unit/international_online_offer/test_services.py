from unittest import mock

from international_online_offer import services
from international_online_offer.core import regions


@mock.patch('international_online_offer.services.get_bci_data_by_dbt_sector')
def test_get_bci_data(client):

    gb_bci_data = services.get_bci_data('Automotive', regions.GB_GEO_CODE)
    # a 5 element tuple should be returned
    assert len(gb_bci_data) == 5

    eng_bci_data = services.get_bci_data('Automotive', regions.ENGLAND_GEO_CODE)
    assert len(eng_bci_data) == 5

    # the api helper should be called twice for each region: 1) retrieve bci data for headline region
    # 2) retrieve bci data for constituent regions
    assert services.get_bci_data_by_dbt_sector.call_count == 4
