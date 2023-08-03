from directory_forms_api_client import actions
from django.conf import settings

from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import (
    choices,
    filter_tags,
    professions,
    regions,
    sectors as sectors,
)


def concat_filters(*filters):
    filters_out = []
    if filters:
        for filter in filters:
            if type(filter) is str:
                filter = [filter]
            if filter is not None:
                filters_out = filters_out + filter
    return filters_out


def find_get_to_know_market_articles(articles, sector_filter, intent_filters):
    filters = concat_filters(sector_filter, intent_filters)
    filtered_pages = []
    for page in articles:
        all_tags = page.specific.tags.all() if hasattr(page.specific.tags, 'all') else page.specific.tags
        tag_match_count = 0
        for tag in all_tags:
            for filter in filters:
                if tag.name == filter:
                    tag_match_count += 1

        if len(all_tags) == tag_match_count and tag_match_count > 0:
            filtered_pages.append(page.specific)

    return filtered_pages


def find_get_support_and_incentives_articles(articles):
    filters = [filter_tags.SUPPORT_AND_INCENTIVES]
    filtered_pages = []
    for page in articles:
        all_tags = page.specific.tags.all() if hasattr(page.specific.tags, 'all') else page.specific.tags
        tag_match_count = 0
        for tag in all_tags:
            for filter in filters:
                if tag.name == filter:
                    tag_match_count += 1

        if len(all_tags) == tag_match_count and tag_match_count > 0:
            filtered_pages.append(page.specific)

    return filtered_pages


def send_welcome_notification(email, form_url):
    action = actions.GovNotifyEmailAction(
        template_id=settings.EYB_ENROLMENT_WELCOME_TEMPLATE_ID,
        email_address=email,
        form_url=form_url,
    )
    response = action.save({})
    response.raise_for_status()
    return response


def find_trade_shows_for_sector(all_trade_shows, sector_filter):
    filters = concat_filters(sector_filter)
    filtered_pages = []
    for page in all_trade_shows:
        all_tags = page.specific.tags.all() if hasattr(page.specific.tags, 'all') else page.specific.tags
        tag_match_count = 0
        for tag in all_tags:
            for filter in filters:
                if tag.name == filter:
                    tag_match_count += 1

        if len(all_tags) == tag_match_count and tag_match_count > 0:
            filtered_pages.append(page.specific)

    return filtered_pages


def get_trade_page(all_trade_pages):
    filtered_pages = []
    for page in all_trade_pages:
        filtered_pages.append(page.specific)
    if len(filtered_pages) > 0:
        return filtered_pages[0]
    return None


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
    }
    mapping = mappings.get(sector)
    return mapping if mapping else []


def get_salary_region_from_region(region):
    # This is the only salary region (from statista, external dataset)
    # that is not quite an exact match to the eyb regions
    if region == regions.EASTERN:
        return 'East'

    for v, d in choices.REGION_CHOICES:
        if v == region:
            return d


def is_authenticated(request):
    if not hasattr(request, 'user'):
        return False

    return request.user.is_authenticated


# flake8: noqa: C901
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
    if executive_salary and mid_salary:
        if executive_salary < mid_salary:
            executive_salary = None

    if executive_salary and entry_salary:
        if executive_salary < entry_salary:
            executive_salary = None

    if mid_salary and entry_salary:
        if mid_salary < entry_salary:
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
