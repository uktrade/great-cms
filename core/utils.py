import re
from datetime import datetime, timezone

from dateutil.relativedelta import relativedelta

trim_page_type = re.compile(r'^([^_]*)_\d*')


def get_all_lessons(module) -> list:
    """
    Helper function to get all lessons of a module (CuratedListPage) that have
    TopicPages between the module and the lessons.

    @returns: List of DetailPage objects (lessons)
    """
    from core.models import DetailPage, TopicPage

    return [
        lesson
        for lesson in DetailPage.objects.live().specific().descendant_of(module)
        if isinstance(lesson.get_parent().specific, TopicPage)
    ]


def get_first_lesson(module):
    """
    Helper function to get first lesson of a module
    @returns: a single DetailPage objects (lesson)
    """
    try:
        return get_all_lessons(module)[0]
    except IndexError:
        return None


class PageTopicHelper:
    """
    Utility class for Page's topic.
    Helper class gathers all info regarding the topic specific
    for the relevant page.
    For example, given a page it calculate the next lesson
    of its topic.

    """

    def __init__(self, page):
        self.page = page
        # This is slightly assumptive of the hierarchy, but we can't
        # import CuratedListPage here:
        self.module = self.page.get_parent().get_parent().specific
        self.page_topic = self.get_page_topic()
        self.module_topics = self.get_module_topics()
        self.module_lessons = get_all_lessons(self.module)

    def get_page_topic(self):
        from core.models import TopicPage

        return TopicPage.objects.live().ancestor_of(self.page).specific().first()

    def get_module_topics(self):
        return self.module.specific.get_topics()

    def total_module_topics(self):
        return self.get_module_topics().count()

    def total_module_lessons(self):
        return len(self.module_lessons) if self.module_lessons else 0

    def get_next_lesson(self):
        lessons = get_all_lessons(self.module)
        if not lessons:
            return
        for i, lesson in enumerate(lessons):
            if self.page.id == lesson.id:
                try:
                    next_lesson = lessons[i + 1]
                    return next_lesson.specific
                except IndexError:
                    return


def choices_to_key_value(choices):
    return [{'value': key, 'label': label} for key, label in choices]


def get_personalised_choices(context):
    """
    Get 'my products' and 'my markets' from user settings
    """
    # from core.helpers import get_trading_blocs_name

    user = context.get('user')
    products = user.get_user_data(name='UserProducts').get('UserProducts')
    markets = user.get_user_data(name='UserMarkets').get('UserMarkets')
    # for market in markets:
    #    if not market.get('trading_bloc'):
    #        market['trading_bloc'] = get_trading_blocs_name(market.get('country_iso2_code'))

    export_commodity_codes = [product.get('commodity_code') for product in products]
    export_markets = [market.get('country_name') for market in markets]
    export_regions = list(dict.fromkeys([market.get('region') for market in markets]))
    return export_commodity_codes, export_markets, export_regions


def split_hs_codes(hs_codes):
    parts = set()
    for hs_code in hs_codes:
        for i in [slice(6), slice(4), slice(2)]:
            parts.add(hs_code[i])
    return parts


def score_name(code):
    return {'6': 'hs6', '4': 'hs4', '2': 'hs2'}.get(str(len(code)))


def rank_hs_codes(cs, commodity_codes, settings):

    score = 0
    split_tags = cs.get('hscodes', '').split(' ')
    if split_tags and split_tags[0] != '':
        for code in split_hs_codes(commodity_codes):
            if code in split_tags:
                score = max(score, getattr(settings, f'product_{score_name(code)}'))
        if score == 0:
            # No match on any product, so reduce the score based on the largest length in cs tags
            score += getattr(settings, f'other_product_{score_name(max(split_tags, key=len))}')
    return score


def rank_tags(cs, user_tags, settings, cs_tag, setting_tag):
    # used for several similar tag sets
    score = 0
    split_tags = cs.get(cs_tag, '').split(' ')
    if split_tags and split_tags[0] != '':
        for user_tag in user_tags:
            if user_tag.replace(' ', '_') in split_tags:
                score = max(score, getattr(settings, setting_tag))
        if score == 0:
            score = score + getattr(settings, f'other_{setting_tag}')
    return score


def rank_related_pages(cs, page_context, settings):
    score = 0
    tagged_pages = cs.get('lesson', '').split(' ')
    if tagged_pages and tagged_pages[0] != '':
        for tagged_page in tagged_pages:
            page_type_match = trim_page_type.match(tagged_page)
            if tagged_page in page_context:
                score = score + getattr(settings, f'{page_type_match.group(1)}')
            else:
                score = score + getattr(settings, f'other_{page_type_match.group(1)}_tags')
    return score


def rank_recency(cs, settings):
    modified = datetime.fromisoformat(cs.get('modified')) if isinstance(cs.get('modified'), str) else cs.get('modified')
    delta = relativedelta(datetime.now(timezone.utc), modified)
    months_old = 12 * delta.years + delta.months
    three_month_block = int(min(int(months_old / 3 + 1) * 3, 24))
    return getattr(settings, f'recency_{three_month_block}_months')


def get_cs_ranking(cs, export_commodity_codes, export_markets, export_regions, page_context, settings):
    score = 0
    score += rank_hs_codes(cs, export_commodity_codes, settings)
    score += rank_tags(cs, export_markets, settings, 'country', 'country_exact')
    score += rank_tags(cs, export_regions, settings, 'region', 'country_region')
    score += rank_related_pages(cs, page_context, settings)
    score += rank_recency(cs, settings)
    return score


"""
def get_cs_score_by_trading_bloc(cs_obj, setting, country):
    from core.helpers import get_trading_blocs_name

    score = 0
    trading_bloc_names = get_trading_blocs_name(country)
    if not trading_bloc_names:
        return score

    cs_tagged_trading_blocs = [str(item) for item in cs_obj.trading_bloc_code_tags.all()]
    if any([item for item in trading_bloc_names if item in cs_tagged_trading_blocs]):
        score = getattr(setting, 'trading_blocs')
    return score
"""
