import pytest

from international_online_offer.dnb.mapping import (
    extract_address,
    extract_company_data,
    extract_trading_names,
)


@pytest.mark.parametrize(
    'input_data, expected',
    [
        # full address without a prefix
        (
            {
                'addressCountry': {
                    'isoAlpha2Code': 'GB',
                },
                'addressLocality': {'name': 'LEEDS'},
                'addressCounty': {
                    'name': 'West Yorkshire',
                },
                'postalCode': 'LS10 2UR',
                'streetAddress': {'line1': 'Leeds street', 'line2': 'Leeds area'},
            },
            {
                'address_line_1': 'Leeds street',
                'address_line_2': 'Leeds area',
                'address_town': 'LEEDS',
                'address_county': 'West Yorkshire',
                'address_postcode': 'LS10 2UR',
                'address_country': 'GB',
            },
        ),
        (
            {
                'addressCountry': {
                    'isoAlpha2Code': 'GB',
                },
                'postalCode': 'LS10 2UR',
                'streetAddress': {},
            },
            {
                'address_line_1': '',
                'address_line_2': '',
                'address_town': '',
                'address_county': '',
                'address_postcode': 'LS10 2UR',
                'address_country': 'GB',
            },
        ),
        # empty address line fields if streetAddress
        # is not a dict
        (
            {
                'addressCountry': {
                    'isoAlpha2Code': 'GB',
                },
                'postalCode': 'LS10 2UR',
                'streetAddress': 'Address1',
            },
            {
                'address_line_1': '',
                'address_line_2': '',
                'address_town': '',
                'address_county': '',
                'address_postcode': 'LS10 2UR',
                'address_country': 'GB',
            },
        ),
        # no fields are required
        (
            {},
            {
                'address_line_1': '',
                'address_line_2': '',
                'address_town': '',
                'address_county': '',
                'address_postcode': '',
                'address_country': '',
            },
        ),
    ],
)
def test_extract_address(input_data, expected):
    assert extract_address(input_data) == expected


@pytest.mark.parametrize(
    'input_data, expected',
    [
        (
            {
                'organization': {},
            },
            [],
        ),
        (
            {
                'organization': {
                    'tradeStyleNames': [
                        {
                            'name': 'Acme Inc.',
                        },
                        {
                            'name': 'Acme Plc.',
                        },
                    ],
                },
            },
            ['Acme Inc.', 'Acme Plc.'],
        ),
    ],
)
def test_extract_trading_names(input_data, expected):
    extract_trading_names(input_data) == expected


def test_company_list_ingest(dnb_company_list_data):
    extracted_data = extract_company_data(dnb_company_list_data['searchCandidates'][0])

    assert extracted_data == {
        'duns_number': '123456789',
        'primary_name': 'Test Company 1',
        'trading_names': [],
        'global_ultimate_duns_number': '',
        'global_ultimate_primary_name': '',
        'domain': 'www.test-display-one.com',
        'address_line_1': 'The Old Test Mill 1',
        'address_line_2': '100 Test Rd',
        'address_town': 'Cheshire',
        'address_county': '',
        'address_postcode': '',
        'address_country': 'GB',
    }


def test_company_list_ingest_street_name(dnb_company_list_data):
    extracted_data = extract_company_data(dnb_company_list_data['searchCandidates'][1])

    assert extracted_data['address_line_1'] == '492 Koller St'
    assert extracted_data['address_line_2'] == 'San Francisco'
