from directory_forms_api_client import actions
from django.conf import settings

from international_online_offer.core import filter_tags


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


def find_opportunities_articles(articles, sector_filter):
    filters = concat_filters(sector_filter, filter_tags.OPPORTUNITY)
    filtered_pages = []
    for page in articles:
        all_tags = page.specific.tags.all() if hasattr(page.specific.tags, 'all') else page.specific.tags
        tag_match_count = 0
        for tag in all_tags:
            for filter in filters:
                if tag.name == filter:
                    tag_match_count += 1

        if len(all_tags) == tag_match_count and len(all_tags) == len(filters) and tag_match_count > 0:
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
