import json

from directory_forms_api_client import actions
from django.conf import settings

from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import (
    choices,
    intents,
    professions,
    regions,
    sectors as sectors,
)


def filter_articles_sector_only(all_sector_tagged_articles):
    sector_only_articles = []
    for page in all_sector_tagged_articles:
        all_tags = page.tags.all() if hasattr(page.tags, 'all') else page.tags
        if len(all_tags) == 1:
            sector_only_articles.append(page)

    return sector_only_articles


def filter_intent_articles_specific_to_sector(all_intent_tagged_articles, sector_filter):
    intent_articles_specific_to_sector = []
    for page in all_intent_tagged_articles:
        all_tags = page.tags.all() if hasattr(page.tags, 'all') else page.tags
        for tag in all_tags:
            if tag.name == sector_filter:
                intent_articles_specific_to_sector.append(page)

    return intent_articles_specific_to_sector


def send_welcome_notification(email, form_url):
    action = actions.GovNotifyEmailAction(
        template_id=settings.EYB_ENROLMENT_WELCOME_TEMPLATE_ID,
        email_address=email,
        form_url=form_url,
    )
    response = action.save({})
    response.raise_for_status()
    return response


def get_trade_assoication_sectors_from_sector(sector):
    mappings = {
        directory_constants_sectors.FOOD_AND_DRINK: [
            'Food and Drink',
        ],
        sectors.TECHNOLOGY_AND_SMART_CITIES: [
            'Artificial Intelligence',
            'Automation',
            'Cyber Security',
            'Electronics and IT Hardware',
            'Engineering',
            'Research',
            'Robotics',
            'Software and IT Services',
            'Solar Energy',
            'Technology',
            'Transport',
        ],
        directory_constants_sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES: [
            'Accounting',
            'Advertising',
            'Financial Services',
            'FinTech',
            'Human Resource Outsourcing',
            'Insurance',
            'Legal Services',
            'Mortgage',
            'Professional Services',
            'Property',
            'Recruitment',
            'Tax',
            'Venture Capital',
        ],
        directory_constants_sectors.CONSUMER_AND_RETAIL: ['Retail'],
        sectors.CREATIVE_INDUSTRIES: [
            'Advertising',
            'Branding',
            'Architecture',
            'Communications',
            'Creative Media',
            'Creative Media/Sports',
            'Design',
            'Education',
            'Electronics and IT Hardware',
            'Fashion',
            'Interior Design',
            'Leisure',
            'Sports',
            'Tourism',
        ],
        directory_constants_sectors.BIOTECHNOLOGY_AND_PHARMACEUTICALS: [
            'Pharmaceuticals',
            'Pharmaceutical',
            'Biotechnology',
        ],
        directory_constants_sectors.ENERGY: ['Energy'],
        directory_constants_sectors.HEALTHCARE_AND_MEDICAL: ['Healthcare', 'Medical'],
        sectors.MEDICAL_DEVICES_AND_EQUIPMENT: ['Medical Device'],
    }
    mapping = mappings.get(sector)
    return mapping if mapping else []


def get_salary_region_from_region(region):
    # This is the only salary region (from statista, external dataset)
    # that is not quite an exact match to the eyb regions
    if region == regions.EAST_OF_ENGLAND:
        return 'East'

    for v, d in choices.REGION_CHOICES:
        if v == region:
            return d


def is_authenticated(request):
    if not hasattr(request, 'user'):
        return False

    return request.user.is_authenticated


def get_salary_data(entry_salary, mid_salary, executive_salary):
    entry_salary = entry_salary.get('median_salary__avg')
    mid_salary = mid_salary.get('median_salary__avg')
    executive_salary = executive_salary.get('median_salary__avg')

    if entry_salary:
        entry_salary = int(entry_salary)
    if mid_salary:
        mid_salary = int(mid_salary)
    if executive_salary:
        executive_salary = int(executive_salary)

    # Change requested to hide salary if numbers are smaller than lower band
    if executive_salary and mid_salary and executive_salary < mid_salary:
        executive_salary = None

    if executive_salary and entry_salary and executive_salary < entry_salary:
        executive_salary = None

    if mid_salary and entry_salary and mid_salary < entry_salary:
        mid_salary = None

    return entry_salary, mid_salary, executive_salary


def get_rent_data(large_warehouse_rent, small_warehouse_rent, shopping_centre, high_street_retail, work_office):
    if large_warehouse_rent:
        large_warehouse_rent = int(large_warehouse_rent.gbp_per_month) if large_warehouse_rent.gbp_per_month else None

    if small_warehouse_rent:
        small_warehouse_rent = int(small_warehouse_rent.gbp_per_month) if small_warehouse_rent.gbp_per_month else None

    if shopping_centre:
        shopping_centre = int(shopping_centre.gbp_per_month) if shopping_centre.gbp_per_month else None

    if high_street_retail:
        high_street_retail = int(high_street_retail.gbp_per_month) if high_street_retail.gbp_per_month else None

    if work_office:
        work_office = int(work_office.gbp_per_month) if work_office.gbp_per_month else None

    return large_warehouse_rent, small_warehouse_rent, shopping_centre, high_street_retail, work_office


def get_sector_professions_by_level(sector):
    for profession_by_sector_and_level in professions.PROFESSIONS_BY_SECTOR_AND_LEVEL:
        if profession_by_sector_and_level['sector'] == sector:
            return profession_by_sector_and_level
    return None


def can_show_salary_component(tags):
    for tag in tags:
        if tag.name == intents.FIND_PEOPLE_WITH_SPECIALIST_SKILLS:
            return True

    return False


def can_show_rent_component(tags):
    for tag in tags:
        if tag.name == intents.SET_UP_NEW_PREMISES or tag.name == intents.SET_UP_A_NEW_DISTRIBUTION_CENTRE:
            return True

    return False


def is_triage_complete(triage_data):
    return bool(
        triage_data
        and triage_data.sector
        and (triage_data.intent or triage_data.intent_other)
        and (triage_data.location or triage_data.location_none)
        and triage_data.hiring
        and (triage_data.spend or triage_data.spend_other)
    )


# Getting region and city choices from json file stored in fixtures
# to use with accessible autocomplete and select input on triage
# location select step, data was pulled from data workspace postcode
# dataset using distinct query on city as CSV and converted to json.


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
                locations_tuple = ((city.replace(' ', '_').upper(), city),) + locations_tuple
        if include_regions:
            locations_tuple = (
                (region_obj['region'].replace(' ', '_').upper(), region_obj['region']),
            ) + locations_tuple
    return locations_tuple


def is_region(choice):
    json_data = get_region_and_cities_json_file()
    for region_obj in json_data:
        if region_obj['region'].replace(' ', '_').upper() == choice:
            return True
    return False


def get_region_from_city(choice):
    json_data = get_region_and_cities_json_file()
    for region_obj in json_data:
        for city in region_obj['cities']:
            if city.replace(' ', '_').upper() == choice:
                return region_obj['region'].replace(' ', '_').upper()

    return ''
