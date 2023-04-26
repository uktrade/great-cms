from international_online_offer.core import filter_tags


def concat_filters(*filters):
    filters_out = []
    for filter in filters:
        if type(filter) is str:
            filter = [filter]
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
