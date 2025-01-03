from directory_forms_api_client import actions
from django.conf import settings

from international_online_offer.core import choices, intents, professions, regions


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
        'Food and drink': [
            'Food and Drink',
        ],
        'Technology and smart cities': [
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
        'Financial and professional services': [
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
        'Consumer and retail': ['Retail'],
        'Creative industries': [
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
        'Pharmaceuticals and biotechnology': [
            'Pharmaceuticals',
            'Pharmaceutical',
            'Biotechnology',
        ],
        'Energy': ['Energy'],
        'Healthcare services': ['Healthcare', 'Medical', 'Health Technology', 'Healthcare Technology', 'Health'],
        'Medical devices and equipment': ['Medical Device'],
        'Education and training': ['Education', 'Training'],
        'Advanced engineering': ['Engineering', 'Advanced Materials & Metals'],
        'Agriculture, horticulture, fisheries and pets': [
            'Agriculture',
            'Agriculture, Horticulture and Fisheries',
            'Food and Drink Agriculture',
            'Agriculture & Manufacturing',
            'Pets',
        ],
        'Railways': ['Rail'],
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


def clean_salary_data(salary_data: dict) -> dict:
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


def get_spend_choices_by_currency(currency):
    spend_choices = choices.SPEND_CHOICES
    if currency == 'EUR':
        spend_choices = choices.SPEND_CHOICES_EURO
    elif currency == 'USD':
        spend_choices = choices.SPEND_CHOICES_USD
    return spend_choices


def get_current_step(user_data, triage_data):
    if not user_data or not triage_data:
        return 'about-your-business'

    find_your_company_step = ['company_name']
    if not user_data.duns_number:
        find_your_company_step += ['address_line_1', 'town']

    triage_steps = {
        'business-headquarters': ['company_location'],
        'find-your-company': find_your_company_step,
        'business-sector': ['sector'],
        'know-setup-location': ['location_none'],
        'when-want-setup': ['landing_timeframe'],
        'intent': ['intent'],
        'hiring': ['hiring'],
        'spend': ['spend'],
        'contact-details': ['full_name', 'role', 'telephone_number'],
    }

    for view_name, fields in triage_steps.items():
        for field in fields:
            value = getattr(user_data, field, getattr(triage_data, field, None))
            if value in (None, '', []):
                return view_name

    return None  # All steps are completed


def is_triage_complete(user_data, triage_data):
    if user_data is None or triage_data is None:
        return False

    if (
        user_data.company_location
        and user_data.company_name
        and (user_data.address_line_1 or user_data.duns_number)
        and user_data.full_name
        and (user_data.town or user_data.duns_number)
        and user_data.role
        and user_data.telephone_number
        and user_data.landing_timeframe
        and triage_data.sector
        and triage_data.location_none is not None
        and triage_data.intent
        and triage_data.spend
        and triage_data.hiring
    ):
        return True

    return False
