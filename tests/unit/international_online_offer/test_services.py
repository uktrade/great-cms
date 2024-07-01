from unittest import mock

from core.tests.helpers import create_response
from international_online_offer import services
from international_online_offer.core import professions, regions


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


@mock.patch(
    'international_online_offer.services.get_salary_data',
    return_value=[
        {
            'geo_description': 'East Midlands',
            'vertical': 'Finance and Professional Services',
            'professional_level': 'Director/Executive',
            'median_salary': 48028,
            'dataset_year': 2022,
        },
        {
            'geo_description': 'East Midlands',
            'vertical': 'Finance and Professional Services',
            'professional_level': 'Entry-level',
            'median_salary': 23678,
            'dataset_year': 2022,
        },
        {
            'geo_description': 'East Midlands',
            'vertical': 'Finance and Professional Services',
            'professional_level': 'Middle/Senior Management',
            'median_salary': 33343,
            'dataset_year': 2022,
        },
    ],
)
def test_get_median_salaries(mock_get_salary_data, client):
    salaries = services.get_median_salaries('Finance and Professional Services')

    assert salaries[professions.ENTRY_LEVEL] == 23678
    assert salaries[professions.MID_SENIOR_LEVEL] == 33343
    assert salaries[professions.DIRECTOR_EXECUTIVE_LEVEL] == 48028
    assert salaries['error_msg'] == ''
    assert mock_get_salary_data.call_count == 1


# first call to get_salary_data returns no data, second call returns data for a different location
@mock.patch(
    'international_online_offer.services.get_salary_data',
    side_effect=[
        [],
        [
            {
                'geo_description': 'East Midlands',
                'vertical': 'Finance and Professional Services',
                'professional_level': 'Middle/Senior Management',
                'median_salary': 33343,
                'dataset_year': 2022,
            }
        ],
    ],
)
def test_get_median_salaries_no_location_data(mock_get_salary_data, client):
    salaries = services.get_median_salaries('Finance and Professional Services', geo_region='London')

    assert salaries[professions.ENTRY_LEVEL] is None
    assert salaries[professions.MID_SENIOR_LEVEL] is None
    assert salaries[professions.DIRECTOR_EXECUTIVE_LEVEL] is None
    assert salaries['error_msg'] == 'No data available for this location.'

    # called twice, 1 x to get inital which is empty, 1 x to check if any sector data
    assert mock_get_salary_data.call_count == 2


@mock.patch('international_online_offer.services.get_salary_data', return_value=[])
def test_get_median_salaries_no_sector_data(mock_get_salary_data, client):
    salaries = services.get_median_salaries('Finance and Professional Services', geo_region='London')

    assert salaries[professions.ENTRY_LEVEL] is None
    assert salaries[professions.MID_SENIOR_LEVEL] is None
    assert salaries[professions.DIRECTOR_EXECUTIVE_LEVEL] is None
    assert salaries['error_msg'] == 'No data available for this sector.'

    # called twice, 1 x to get inital which is empty, 1 x to check if any sector data
    assert mock_get_salary_data.call_count == 2


@mock.patch(
    'directory_api_client.api_client.dataservices.get_eyb_commercial_rent_data',
    return_value=create_response(
        [
            {
                'geo_description': 'London',
                'vertical': 'Industrial',
                'sub_vertical': 'Large Warehouses',
                'gbp_per_square_foot_per_month': 2.292,
                'square_feet': 340000.000,
                'gbp_per_month': 779166.667,
                'dataset_year': 2023,
            },
            {
                'geo_description': 'London',
                'vertical': 'Retail',
                'sub_vertical': 'Prime shopping centre',
                'gbp_per_square_foot_per_month': 14.443,
                'square_feet': 2195.000,
                'gbp_per_month': 31702.791,
                'dataset_year': 2023,
            },
            {
                'geo_description': 'London',
                'vertical': 'Retail',
                'sub_vertical': 'High Street Retail',
                'gbp_per_square_foot_per_month': 74.722,
                'square_feet': 2195.000,
                'gbp_per_month': 164015.278,
                'dataset_year': 2023,
            },
            {
                'geo_description': 'London',
                'vertical': 'Office',
                'sub_vertical': 'Work Office',
                'gbp_per_square_foot_per_month': None,
                'square_feet': 16671.000,
                'gbp_per_month': None,
                'dataset_year': 2023,
            },
        ]
    ),
)
def test_get_rent_data(client):
    rent_data_from_api = services.get_rent_data('London')

    # from above
    rent_values = [779166.667, None, 31702.791, 164015.278, None]

    assert len(rent_data_from_api) == 5

    for idx, rent_value in enumerate(rent_values):
        assert rent_data_from_api[idx] == rent_value
