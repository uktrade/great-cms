import json

# Getting region and city choices from json file stored in fixtures
# to use with accessible autocomplete and select input on triage
# location select step, data was pulled from data workspace postcode
# dataset using distinct query on city as CSV and converted to json.

# function used to help convert display / human readable strings from
# json file into literals similar to that of the ones in
# directory-constants. Important as this is what we map to


def to_literal(value_in):
    return value_in.replace(' ', '_').replace(',', '').replace('.', '').replace("'", '').upper()


def get_region_and_cities_json_file():
    json_data = open('international_online_offer/fixtures/regions-and-cities.json')
    deserialised_data = json.load(json_data)
    json_data.close()
    return deserialised_data


def get_region_and_cities_json_file_as_string():
    json_data = get_region_and_cities_json_file()
    json_data_string = json.dumps(json_data)
    return json_data_string


def generate_location_choices(include_regions=True, include_cities=True):
    # Django only takes tuples (actual value, human readable name) so we need to
    # repack the json in a dictionay of tuples for cities

    json_data = get_region_and_cities_json_file()
    json_data = sorted(json_data, key=lambda x: x['region'], reverse=True)

    locations_tuple = ()
    for region_obj in json_data:
        if include_cities:
            for city in region_obj['cities']:
                locations_tuple = ((to_literal(city), city),) + locations_tuple
        if include_regions:
            locations_tuple = ((to_literal(region_obj['region']), region_obj['region']),) + locations_tuple
    return locations_tuple


def is_region(choice):
    json_data = get_region_and_cities_json_file()
    for region_obj in json_data:
        if to_literal(region_obj['region']) == choice:
            return True
    return False


def get_region_from_city(choice):
    json_data = get_region_and_cities_json_file()
    for region_obj in json_data:
        for city in region_obj['cities']:
            if to_literal(city) == choice:
                return to_literal(region_obj['region'])

    return ''


# Getting sectors and SIC sectors within those choices from json file stored in fixtures
# to use with accessible autocomplete and select input on sector
# select step, data was pulled from data workspace sector to sic
# dataset exported as json


def get_sectors_and_sic_sectors_file():
    json_data = open('international_online_offer/fixtures/sectors-and-sic-sectors.json')
    deserialised_data = json.load(json_data)
    json_data.close()
    return deserialised_data


def get_sectors_as_string(json_data):
    json_data_string = json.dumps(json_data)
    return json_data_string


def get_sectors_and_sic_sectors_file_as_string():
    json_data = get_sectors_and_sic_sectors_file()
    json_data_string = json.dumps(json_data)
    return json_data_string


def generate_sector_choices():
    # Django only takes tuples (actual value, human readable name) so we need to
    # repack the json in a dictionay of tuples for dbt sectors

    json_data = get_sectors_and_sic_sectors_file()
    distinct_list_of_sectors = []
    for sic_obj in json_data['data']:
        sector = sic_obj['dit_sector_list_field_04']
        if sector not in distinct_list_of_sectors:
            distinct_list_of_sectors.append(sector)

    distinct_list_of_sectors.sort()

    sectors_tuple = ()
    for sector in distinct_list_of_sectors:
        sectors_tuple = ((to_literal(sector), sector),) + sectors_tuple
    return sectors_tuple


def generate_sector_sic_choices():
    # Django only takes tuples (actual value, human readable name) so we need to
    # repack the json in a dictionay of tuples for SIC sectors

    json_data = get_sectors_and_sic_sectors_file()
    # json_data = sorted(json_data['data'], key=lambda x: x['region'], reverse=True)

    sic_sectors_tuple = ()
    for sic_obj in json_data['data']:
        sic_sectors_tuple = ((to_literal(sic_obj['sic_description']), sic_obj['sic_description']),) + sic_sectors_tuple
    return sic_sectors_tuple


def get_parent_sectors(sectors_json):
    parent_sectors = []
    for sector_row in sectors_json:
        if sector_row['sector_name'] not in parent_sectors:
            parent_sectors.append(sector_row['sector_name'])

    parent_sectors.sort()
    return parent_sectors


def get_parent_sectors_choices(parent_sectors):
    sectors_tuple = ()
    for sector in parent_sectors:
        sectors_tuple = ((sector, sector),) + sectors_tuple
    return sectors_tuple


def get_sub_sectors(sectors_json):
    sub_sectors = []
    for sector_row in sectors_json:
        if sector_row['sub_sector_name'] and sector_row['sub_sector_name'] not in sub_sectors:
            sub_sectors.append(sector_row['sub_sector_name'])

    sub_sectors.sort()
    return sub_sectors


def get_sub_sectors_choices(sub_sectors):
    sectors_tuple = ()
    for sector in sub_sectors:
        sectors_tuple = ((sector, sector),) + sectors_tuple
    return sectors_tuple


def get_sub_sub_sectors(sectors_json):
    sub_sub_sectors = []
    for sector_row in sectors_json:
        if sector_row['sub_sub_sector_name'] and sector_row['sub_sub_sector_name'] not in sub_sub_sectors:
            sub_sub_sectors.append(sector_row['sub_sub_sector_name'])

    sub_sub_sectors.sort()
    return sub_sub_sectors


def get_sub_sub_sectors_choices(sub_sub_sectors):
    sectors_tuple = ()
    for sector in sub_sub_sectors:
        sectors_tuple = ((sector, sector),) + sectors_tuple
    return sectors_tuple


def get_sub_and_sub_sub_sectors_choices(sectors_json):
    sectors_tuple = ()
    for sector_row in sectors_json:
        sub_sector = sector_row['sub_sector_name']
        if sub_sector:
            sub_sub_sector = sector_row['sub_sub_sector_name']
            if not sub_sub_sector:
                sectors_tuple = ((sector_row['sector_id'], sub_sector),) + sectors_tuple
            else:
                sectors_tuple = ((sector_row['sector_id'], sub_sub_sector),) + sectors_tuple

    return sectors_tuple


def get_sector_from_sic_sector(choice):
    json_data = get_sectors_and_sic_sectors_file()
    for sic_obj in json_data['data']:
        if to_literal(sic_obj['sic_description']) == choice:
            return to_literal(sic_obj['dit_sector_list_field_04'])

    return ''


def get_sectors_by_selected_id(sectors_json, selected_sector_id):
    for sector_row in sectors_json:
        if sector_row['sector_id'] == selected_sector_id:
            return sector_row['sector_name'], sector_row['sub_sector_name'], sector_row['sub_sub_sector_name']


def get_full_sector_name_from_sic_sector(choice):
    json_data = get_sectors_and_sic_sectors_file()
    for sic_obj in json_data['data']:
        if to_literal(sic_obj['sic_description']) == choice:
            return sic_obj['dit_sector_list_full_sector_name']

    return ''
