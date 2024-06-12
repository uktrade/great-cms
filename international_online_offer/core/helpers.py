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
        sectors.PHARMACEUTICALS_AND_BIOTECHNOLOGY: [
            'Pharmaceuticals',
            'Pharmaceutical',
            'Biotechnology',
        ],
        directory_constants_sectors.ENERGY: ['Energy'],
        sectors.HEALTHCARE_SERVICES: ['Healthcare', 'Medical', 'Health Technology', 'Healthcare Technology', 'Health'],
        sectors.MEDICAL_DEVICES_AND_EQUIPMENT: ['Medical Device'],
        directory_constants_sectors.EDUCATION_AND_TRAINING: ['Education', 'Training'],
        sectors.ADVANCED_ENGINEERING: ['Engineering', 'Advanced Materials & Metals'],
        sectors.AGRICULTURE_HORTICULTURE_FISHERIES_AND_PETS: [
            'Agriculture',
            'Agriculture, Horticulture and Fisheries',
            'Food and Drink Agriculture',
            'Agriculture & Manufacturing',
            'Pets',
        ],
        directory_constants_sectors.RAILWAYS: ['Rail'],
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


def clean_salary_data(salary_data: dict) -> dict:
    # largely the same method as above, can delete above get_salary_data() post election
    result = {**salary_data}
    entry_salary = salary_data.get(professions.ENTRY_LEVEL)
    mid_salary = salary_data.get(professions.MID_SENIOR_LEVEL)
    executive_salary = salary_data.get(professions.DIRECTOR_EXECUTIVE_LEVEL)

    # Change requested to hide salary if numbers are smaller than lower band
    if executive_salary and mid_salary and executive_salary < mid_salary:
        del result[professions.DIRECTOR_EXECUTIVE_LEVEL]
    elif executive_salary and entry_salary and executive_salary < entry_salary:
        del result[professions.DIRECTOR_EXECUTIVE_LEVEL]

    if mid_salary and entry_salary and mid_salary < entry_salary:
        del result[professions.MID_SENIOR_LEVEL]

    return result


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
