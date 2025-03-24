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

    locations_tuple = ()
    for region_obj in json_data:
        if include_cities:
            for city in region_obj['cities']:
                locations_tuple = ((to_literal(city), city),) + locations_tuple
        if include_regions:
            locations_tuple = ((to_literal(region_obj['region']), region_obj['region_display']),) + locations_tuple

    # return result set sorted alphabetically
    return tuple(sorted(locations_tuple))


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


def get_sectors_as_string(json_data):
    json_data_string = json.dumps(json_data)
    return json_data_string


def get_sector(sector_id, sectors):
    for sector in sectors:
        if sector['sector_id'] == sector_id:
            return sector


def get_full_sector_names_as_choices(sectors_json):
    # First, sort the sector names alphabetically (A-Z)
    sorted_sectors = sorted(sectors_json, key=lambda x: x['full_sector_name'])

    # Create the tuple of choices, each choice is a tuple of (value, label)
    sectors_tuple = tuple((sector['full_sector_name'], sector['full_sector_name']) for sector in sorted_sectors)

    return sectors_tuple


def get_sectors_as_choices(sectors_json):
    sectors_tuple = ()
    for sector_row in sectors_json:
        parent_sector = sector_row['sector_name']
        child_sector = sector_row['sub_sector_name']
        grandchild_sector = sector_row['sub_sub_sector_name']

        if grandchild_sector:
            sectors_tuple = ((sector_row['sector_id'], grandchild_sector),) + sectors_tuple
            continue

        if child_sector:
            sectors_tuple = ((sector_row['sector_id'], child_sector),) + sectors_tuple
            continue

        sectors_tuple = ((sector_row['sector_id'], parent_sector),) + sectors_tuple

    return sectors_tuple


def get_parent_sectors_as_choices(sectors_json):
    sectors_tuple = ()
    for sector_row in sectors_json:
        parent_sector = sector_row['sector_name']
        child_sector = sector_row['sub_sector_name']
        if not child_sector:
            sectors_tuple = ((parent_sector, parent_sector),) + sectors_tuple

    return sectors_tuple


def get_sectors_by_selected_id(sectors_json, selected_sector_id):
    for sector_row in sectors_json:
        if sector_row['sector_id'] == selected_sector_id:
            return sector_row['sector_name'], sector_row['sub_sector_name'], sector_row['sub_sub_sector_name']
