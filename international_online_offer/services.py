from typing import Dict, List, Tuple

from directory_api_client import api_client
from international_online_offer.core import regions
from international_online_offer.core.professions import (
    DIRECTOR_EXECUTIVE_LEVEL,
    ENTRY_LEVEL,
    MID_SENIOR_LEVEL,
)


def get_bci_data_by_dbt_sector(dbt_sector_name: str, geo_codes: List[str] = None) -> Dict:
    """
    API helper function for getting BCI data by DBT sector
    """
    response = api_client.dataservices.get_business_cluster_information_by_dbt_sector(
        dbt_sector_name, geo_code=','.join(geo_codes)
    )

    if response.status_code != 200:
        return None

    return response.json()


def get_bci_data(dbt_sector_name: str, area: str) -> Tuple[Dict, Dict, Dict, int, List]:
    """
    Get BCI data in a front-end friendly format. The screen designs consist of a headline parent area (e.g. UK)
    followed by a list of child regions (e.g. England, Scotland, Wales, Northern Ireland). Population details for
    each headline area are hardcoded and obtained from ONS.

    Input parameters:
        dbt_sector_name -> a DBT sector
        area -> a geocode which represents the parent area

    Output:
        A tuple containing:
            bci_headline -> stats to display as the parent region for the page
            headline_region -> human friendly region name / population
            bci_detail -> list of stats to display for each region
            bci_release_year -> release year of data
            hyperlinked_geo_codes -> list of geo codes to display as hyperlinks
    """

    bci_headline: Dict = None
    bci_detail: Dict = None
    hyperlinked_geo_codes: List = []
    bci_release_year: int = None
    headline_region: Dict = {}
    bci_sector: str = dbt_sector_name.replace('_', ' ')

    if area == regions.GB_GEO_CODE:
        bci_headline = get_bci_data_by_dbt_sector(bci_sector, geo_codes=[regions.GB_GEO_CODE])
        bci_detail = get_bci_data_by_dbt_sector(
            bci_sector,
            geo_codes=[
                regions.ENGLAND_GEO_CODE,
                regions.SCOTLAND_GEO_CODE,
                regions.WALES_GEO_CODE,
                regions.NORTHERN_IRELAND_GEO_CODE,
            ],
        )
        hyperlinked_geo_codes = [regions.ENGLAND_GEO_CODE]
        headline_region = {'name': 'UK nations', 'sub_area_table_header': 'Nation', 'population_million': 67}
    elif area == regions.ENGLAND_GEO_CODE:
        bci_headline = get_bci_data_by_dbt_sector(bci_sector, geo_codes=[regions.ENGLAND_GEO_CODE])
        bci_detail = get_bci_data_by_dbt_sector(
            bci_sector,
            geo_codes=[
                regions.EAST_MIDLANDS_GEO_CODE,
                regions.LONDON_GEO_CODE,
                regions.NORTH_EAST_GEO_CODE,
                regions.NORTH_WEST_GEO_CODE,
                regions.SOUTH_EAST_GEO_CODE,
                regions.SOUTH_WEST_GEO_CODE,
                regions.WEST_MIDLANDS_GEO_CODE,
                regions.YORKSHIRE_AND_THE_HUMBER_GEO_CODE,
                regions.EAST_GEO_CODE,
            ],
        )
        hyperlinked_geo_codes = []
        headline_region = {
            'name': 'English regions',
            'sub_area_table_header': 'Region',
            'population_million': 56.5,
        }

    if bci_headline and len(bci_headline) > 0:
        # there can only be one headline
        bci_headline = bci_headline[0]
        bci_release_year = bci_headline['business_count_release_year']

    return (bci_headline, headline_region, bci_detail, bci_release_year, hyperlinked_geo_codes)


def get_salary_data(vertical: str, professional_level: str = None, geo_region: str = None):

    response = api_client.dataservices.get_eyb_salary_data(vertical, professional_level, geo_region)

    return response.json()


def get_median_salaries(vertical: str, professional_level: str = None, geo_region: str = None) -> Dict:
    error_msg = ''
    all_salaries = get_salary_data(vertical, professional_level=professional_level, geo_region=geo_region)

    if len(all_salaries) == 0:
        data_for_vertical = get_salary_data(vertical)
        error_msg = (
            'No data available for this sector.'
            if len(data_for_vertical) == 0
            else 'No data available for this location.'
        )

    # if iterator returns no values, return an empty dictonary so that it can be used with the .get function
    entry_salary = next((salary for salary in all_salaries if salary['professional_level'] == ENTRY_LEVEL), {})
    mid_salary = next((salary for salary in all_salaries if salary['professional_level'] == MID_SENIOR_LEVEL), {})
    executive_salary = next(
        (salary for salary in all_salaries if salary['professional_level'] == DIRECTOR_EXECUTIVE_LEVEL), {}
    )

    return {
        'error_msg': error_msg,
        ENTRY_LEVEL: entry_salary.get('median_salary'),
        MID_SENIOR_LEVEL: mid_salary.get('median_salary'),
        DIRECTOR_EXECUTIVE_LEVEL: executive_salary.get('median_salary'),
    }


def get_rent_data(geo_region: str, vertical: str = None, sub_vertical: str = None) -> Tuple:

    response = api_client.dataservices.get_eyb_commercial_rent_data(geo_region, vertical, sub_vertical)

    rent_data = response.json()

    # if iterator returns no values, return an empty dictonary so that it can be used with the .get function
    large_warehouse = next((rent for rent in rent_data if rent['sub_vertical'] == 'Large Warehouses'), {})
    small_warehouse = next((rent for rent in rent_data if rent['sub_vertical'] == 'Small Warehouses'), {})
    shopping_centre = next((rent for rent in rent_data if rent['sub_vertical'] == 'Prime shopping centre'), {})
    high_street_retail = next((rent for rent in rent_data if rent['sub_vertical'] == 'High Street Retail'), {})
    work_office = next((rent for rent in rent_data if rent['sub_vertical'] == 'Work Office'), {})

    return (
        large_warehouse.get('gbp_per_month'),
        small_warehouse.get('gbp_per_month'),
        shopping_centre.get('gbp_per_month'),
        high_street_retail.get('gbp_per_month'),
        work_office.get('gbp_per_month'),
    )


def get_dbt_sectors():
    response = api_client.dataservices.get_dbt_sectors()
    return response.json()
