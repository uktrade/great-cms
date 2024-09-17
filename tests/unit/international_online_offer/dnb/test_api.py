from unittest import mock

from international_online_offer.dnb.api import (
    company_list_search,
    company_typeahead_search,
)
from tests.unit.core.test_helpers import create_response


@mock.patch('international_online_offer.dnb.api.api_request')
def test_company_list_search(mock_api_request, dnb_company_list_data):
    mock_api_request.return_value = create_response(dnb_company_list_data)

    output = company_list_search({'searchTerm': 'hello world'})

    assert output['total_matches'] == 2
    assert output['total_returned'] == 2
    assert output['page_size'] == 0
    assert output['page_number'] == 1
    assert len(output['results']) == 2

    assert mock_api_request.call_args[0] == ('POST', '/v1/search/companyList')
    assert mock_api_request.call_args[1]['kwargs'] == {'json': {'searchTerm': 'hello world'}}


@mock.patch('international_online_offer.dnb.api.api_request')
def test_company_typeahead_search(mock_api_request, dnb_company_list_data):
    mock_api_request.return_value = create_response(dnb_company_list_data)

    output = company_typeahead_search({'searchTerm': 'acomp', 'country': 'ES'})

    assert output['total_matches'] == 2
    assert output['total_returned'] == 2
    assert output['page_size'] == 0
    assert output['page_number'] == 1
    assert len(output['results']) == 2

    assert mock_api_request.call_args[0] == ('GET', '/v1/search/typeahead')
    assert mock_api_request.call_args[1]['kwargs'] == {'params': {'searchTerm': 'acomp', 'country': 'ES'}}
