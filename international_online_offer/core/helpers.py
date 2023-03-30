def find_get_to_know_market_articles(articles, sector_filter, intent_filters):
    filtered_pages = []
    filters = concat_filters(sector_filter, intent_filters)
    for page in articles:
        all_tags = page.specific.tags.all()
        tag_match_count = 0
        for tag in all_tags:
            for filter in filters:
                if tag.name == filter:
                    tag_match_count += 1

        if len(all_tags) == tag_match_count:
            filtered_pages.append(page.specific)

    return filtered_pages


def concat_filters(sector_filter, intent_filters):
    sector_filter = [sector_filter]
    return sector_filter + intent_filters
