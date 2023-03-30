def find_get_to_know_market_articles(articles, sector_filter, intent_filters):
    filtered_pages = []
    for page in articles:
        for tag in page.specific.tags.all():
            if tag.name == sector_filter:
                filtered_pages.append(page.specific)
                break
            if tag.name in intent_filters:
                filtered_pages.append(page.specific)
                break
    return filtered_pages
