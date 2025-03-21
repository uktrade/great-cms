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
        return 'east'

    for v, _ in choices.REGION_CHOICES:
        if v == region:
            return v.lower().replace('_', ' ')


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
        and (user_data.town or user_data.duns_number)
        and user_data.landing_timeframe
        and triage_data.sector
        and triage_data.location_none is not None
        and triage_data.intent
        and triage_data.spend
        and triage_data.hiring
    ):
        return True

    return False


def get_hero_image_by_sector(sector):
    base_path = '/static/img/dynamic-guide-hero-images/'
    file_type = '.jpg'
    sector_to_image_map = {
        'Advanced engineering': f'hero-advanced-manufacturing{file_type}',
        'Aerospace': f'hero-aerospace{file_type}',
        'Agriculture, horticulture, fisheries and pets': f'hero-agriculture{file_type}',
        'Airports': f'hero-airports{file_type}',
        'Automotive': f'hero-automotive{file_type}',
        'Chemicals': f'hero-chemicals{file_type}',
        'Construction': f'hero-construction{file_type}',
        'Consumer and retail': f'hero-retail{file_type}',
        'Creative industries': f'hero-creative{file_type}',
        'Defence': f'hero-defence{file_type}',
        'Education and training': f'hero-education{file_type}',
        'Energy': f'hero-energy{file_type}',
        'Environment': f'hero-environment{file_type}',
        'Financial and professional services': f'hero-finance{file_type}',
        'Food and drink': f'hero-food-and-drink{file_type}',
        'Healthcare services': f'hero-health-and-pharma{file_type}',
        'Logistics': f'hero-logistics{file_type}',
        'Maritime': f'hero-maritime{file_type}',
        'Medical devices and equipment': f'hero-health-and-pharma{file_type}',
        'Mining': f'hero-mining{file_type}',
        'Pharmaceuticals and biotechnology': f'hero-health-and-pharma{file_type}',
        'Railways': f'hero-rail{file_type}',
        'Security': f'hero-security{file_type}',
        'Space': f'hero-space{file_type}',
        'Sports economy': f'hero-sport{file_type}',
        'Technology and smart cities': f'hero-tech{file_type}',
        'Water': f'hero-water{file_type}',
    }
    # we dont have a default image so will use finance as fallback cause I like it
    return f'{base_path}{sector_to_image_map.get(sector, "hero-finance.jpg")}'


def get_region_map_image_by_region(region):
    base_path = '/static/svg/regions/'
    file_type = '.svg'
    region_to_image_map = {
        regions.EAST_OF_ENGLAND: f'uk-england-east{file_type}',
        regions.EAST_MIDLANDS: f'uk-england-east-midlands{file_type}',
        regions.LONDON: f'uk-england-london{file_type}',
        regions.NORTH_EAST: f'uk-england-north-east{file_type}',
        regions.NORTH_WEST: f'uk-england-north-west{file_type}',
        regions.NORTHERN_IRELAND: f'uk-northern-ireland{file_type}',
        regions.SOUTH_EAST: f'uk-england-south-east{file_type}',
        regions.SOUTH_WEST: f'uk-england-south-west{file_type}',
        regions.SCOTLAND: f'uk-scotland{file_type}',
        regions.WALES: f'uk-wales{file_type}',
        regions.WEST_MIDLANDS: f'uk-england-west-midlands{file_type}',
        regions.YORKSHIRE_AND_THE_HUMBER: f'uk-england-yorkshire-and-the-humber{file_type}',
    }
    return f'{base_path}{region_to_image_map.get(region, "uk-all.svg")}'


def get_premises_image_by_sector(sector):
    base_path = 'svg/sector-premises/'
    file_type = '.svg'
    sector_to_image_map = {
        'Advanced engineering': f'icon-premises-advanced-engineering{file_type}',
        'Aerospace': f'icon-premises-aerospace{file_type}',
        'Agriculture, horticulture, fisheries and pets': f'icon-premises-agriculture{file_type}',
        'Airports': f'icon-premises-airport{file_type}',
        'Automotive': f'icon-premises-automotive{file_type}',
        'Chemicals': f'icon-premises-chemicals{file_type}',
        'Construction': f'icon-premises-construction{file_type}',
        'Consumer and retail': f'icon-premises-retail{file_type}',
        'Creative industries': f'icon-premises-creative{file_type}',
        'Defence': f'icon-premises-defence{file_type}',
        'Education and training': f'icon-premises-education{file_type}',
        'Energy': f'icon-premises-energy{file_type}',
        'Environment': f'icon-premises-environment{file_type}',
        'Financial and professional services': f'icon-premises-finance{file_type}',
        'Food and drink': f'icon-premises-food{file_type}',
        'Healthcare services': f'icon-premises-health{file_type}',
        'Logistics': f'icon-premises-logistics{file_type}',
        'Maritime': f'icon-premises-maritime{file_type}',
        'Medical devices and equipment': f'icon-premises-health{file_type}',
        'Mining': f'icon-premises-mining{file_type}',
        'Pharmaceuticals and biotechnology': f'icon-premises-health{file_type}',
        'Railways': f'icon-premises-rail{file_type}',
        'Security': f'icon-premises-security{file_type}',
        'Space': f'icon-premises-space{file_type}',
        'Sports economy': f'icon-premises-sport{file_type}',
        'Technology and smart cities': f'icon-premises-tech{file_type}',
        'Water': f'icon-premises-water{file_type}',
    }
    # we dont have a default image so will use agriculture as fallback cause I like it
    return f'{base_path}{sector_to_image_map.get(sector, "icon-premises-agriculture.svg")}'


def get_talent_image_by_sector(sector):
    base_path = 'svg/sector-talent/'
    file_type = '.svg'
    sector_to_image_map = {
        'Advanced engineering': f'icon-talent-advanced-engineering{file_type}',
        'Aerospace': f'icon-talent-aerospace{file_type}',
        'Agriculture, horticulture, fisheries and pets': f'icon-talent-agriculture{file_type}',
        'Airports': f'icon-talent-airport{file_type}',
        'Automotive': f'icon-talent-automotive{file_type}',
        'Chemicals': f'icon-talent-chemicals{file_type}',
        'Construction': f'icon-talent-construction{file_type}',
        'Consumer and retail': f'icon-talent-retail{file_type}',
        'Creative industries': f'icon-talent-creative{file_type}',
        'Defence': f'icon-talent-defence{file_type}',
        'Education and training': f'icon-talent-education{file_type}',
        'Energy': f'icon-talent-energy{file_type}',
        'Environment': f'icon-talent-environment{file_type}',
        'Financial and professional services': f'icon-talent-finance{file_type}',
        'Food and drink': f'icon-talent-food{file_type}',
        'Healthcare services': f'icon-talent-health{file_type}',
        'Logistics': f'icon-talent-logistics{file_type}',
        'Maritime': f'icon-talent-maritime{file_type}',
        'Medical devices and equipment': f'icon-talent-health{file_type}',
        'Mining': f'icon-talent-mining{file_type}',
        'Pharmaceuticals and biotechnology': f'icon-talent-health{file_type}',
        'Railways': f'icon-talent-rail{file_type}',
        'Security': f'icon-talent-security{file_type}',
        'Space': f'icon-talent-space{file_type}',
        'Sports economy': f'icon-talent-sport{file_type}',
        'Technology and smart cities': f'icon-talent-tech{file_type}',
        'Water': f'icon-talent-water{file_type}',
    }
    # we dont have a default image so will use creative as fallback cause I like it
    return f'{base_path}{sector_to_image_map.get(sector, "icon-talent-creative.svg")}'
