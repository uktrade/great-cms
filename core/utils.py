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


def get_personalised_choices(export_plan):
    """
    function to get selected choices from export_plan object

    @param export_plan: export_plan object
    @return: tuple of commodity_code, country, region
    """

    hs_tag, country, region = None, None, None

    if not export_plan:
        return hs_tag, country, region

    export_commodity_codes = export_plan.get('export_commodity_codes', [])
    if export_commodity_codes:
        hs_tag = export_commodity_codes[0]['commodity_code']

    export_countries = export_plan.get('export_countries', [])
    if export_countries:
        country = export_countries[0]['country_iso2_code']
        region = export_countries[0]['region']

    return hs_tag, country, region


def create_filter_dict(product_code=None, country=None, region=None, trading_bloc=None):
    """
     Helper function to create filter dict based on product and target area

    @param product_code: HS code ( HS6, HS4 or HS2)
    @param target_area: country_iso or region, trading_bloc
    @return: dict
    """

    result = dict()
    if product_code:
        result['hs_code_tags__name'] = product_code
    if country:
        result['country_code_tags__name'] = country
    if region:
        result['region_code_tags__name'] = region
    if trading_bloc:
        result['trading_bloc_code_tags__name'] = trading_bloc
    return result


def get_personalised_case_study_orm_filter_args(hs_code=None, country=None, region=None):
    """
    Helper function to generate filter criteria for ORM query to get
    personalised case study

    @param hs_code: HS code (hs6, hs4 or hs2)
    @param country: country iso2 code
    @param region: region of the selected country ( for example 'Asia')
    @return: filter dict
    """
    from core.helpers import get_trading_blocs_name

    filter_args, unique_hs_codes, trading_blocs = [], [], None
    if hs_code:
        hs_codes = [hs_code[i] for i in [slice(6), slice(4), slice(2)]]
        # Removing identical item while keeping order of item
        unique_hs_codes = sorted(set(hs_codes), key=hs_codes.index)

        for code in unique_hs_codes:
            filter_args += [create_filter_dict(product_code=code, country=country)] if country else []
            filter_args += [(create_filter_dict(product_code=code, region=region))] if region else []
            filter_args += [(create_filter_dict(product_code=code))]  # solo hs_lookup

    filter_args += [(create_filter_dict(country=country))] if country else []
    filter_args += [create_filter_dict(region=region)] if region else []

    if country:
        trading_blocs = get_trading_blocs_name(country)
        if trading_blocs:
            filter_args += [create_filter_dict(trading_bloc=area) for area in trading_blocs]

    return [i for i in filter_args if i]


def choices_to_key_value(choices):
    return [{'value': key, 'label': label} for key, label in choices]


def get_most_ranked_case_study(cs_queryset, context):
    from core.models import CaseStudyScoringSettings

    cs_score = dict()
    setting = CaseStudyScoringSettings.for_request(context['request'])
    hs_code, country, region = get_personalised_choices(context['export_plan'])

    for cs_obj in cs_queryset:
        cs_score[cs_obj] = 0
        # scoring by related pages (module, lesson, topic)
        cs_score[cs_obj] += get_cs_score_by_related_page(cs_obj=cs_obj, context=context, setting=setting)
        # scoring by hs_codes
        if hs_code:
            cs_score[cs_obj] += get_cs_score_by_hs_codes(cs_obj=cs_obj, setting=setting, hs_code=hs_code)
        # scoring by region
        if country and region:
            cs_score[cs_obj] += get_cs_score_by_region(cs_obj=cs_obj, setting=setting, country=country, region=region)
        # scoring by trading bloc
        cs_score[cs_obj] += get_cs_score_by_trading_bloc(cs_obj=cs_obj, setting=setting, country=country)
        # recency score
        cs_score[cs_obj] += get_cs_score_by_recency(cs_obj=cs_obj, setting=setting)

    case_study = max(cs_score, key=cs_score.get)
    # case study need to score above threshold
    if cs_score[case_study] >= getattr(setting, 'threshold'):
        return case_study


def get_cs_score_by_recency(cs_obj, setting):
    from datetime import datetime, timezone

    recency = month_delta(cs_obj.modified, datetime.now(timezone.utc))

    return getattr(setting, f'recency_{map_recency_months(recency)}_months')


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


def get_cs_score_by_related_page(cs_obj, context, setting):
    score = 0
    tagged_pages = [related_page.page.specific for related_page in cs_obj.related_pages.all()]
    if not tagged_pages:
        return score

    page_mapping = {'lesson': 'detailpage', 'module': 'curatedlistpage', 'topic': 'topicpage'}
    for page_type in ['lesson', 'module', 'topic']:
        all_page_type = [item for item in tagged_pages if page_mapping.get(page_type) == item.specific._meta.model_name]
        # Positive Scoring
        for page in all_page_type:
            if page == context[f'current_{page_type}']:
                score += getattr(setting, f'{page_type}')
            else:
                score += getattr(setting, f'other_{page_type}_tags')

    return score


def get_cs_score_by_hs_codes(cs_obj, setting, hs_code):
    score = 0
    hs6, hs4, hs2 = (hs_code[i] for i in [slice(6), slice(4), slice(2)] if hs_code)
    tagged_hs_codes = [str(item) for item in cs_obj.hs_code_tags.all()]
    for hs_item in ['hs6', 'hs4', 'hs2']:
        if eval(hs_item) in tagged_hs_codes:
            score += getattr(setting, f'product_{hs_item}')

        # dampening scoring
        dampening_hs_list = [i for i in tagged_hs_codes if i != hs6]
        for code in dampening_hs_list:
            score += getattr(setting, f'other_product_{hs_item}')

    return score


def get_cs_score_by_region(cs_obj, setting, country, region):
    score = 0
    region_mapping = {'country': 'country_exact', 'region': 'country_region'}
    cs_tagged_regions = [str(item) for item in cs_obj.country_code_tags.all()]
    for region_key, region_setting in region_mapping.items():
        # positive scoring
        if eval(region_key) in cs_tagged_regions:
            score += getattr(setting, region_setting)
        dampening_country_list = [item for item in cs_tagged_regions if len(item) == 2 and item != country]
        # dampening scoring
        if region_key == 'country':
            for other_item in dampening_country_list:
                score += getattr(setting, f'other_{region_setting}')
        else:
            dampening_region_list = [item for item in cs_tagged_regions if len(item) != 2 and item != region]
            for other_item in dampening_region_list:
                score += getattr(setting, f'other_{region_setting}')

    return score


def month_delta(start_date, end_date):
    """
    Helper method to check different in month for given two dates
    """
    from dateutil.relativedelta import relativedelta

    delta = relativedelta(end_date, start_date)
    return 12 * delta.years + delta.months


def map_recency_months(month):
    """
    Helper method to decide which month should be applied for scoring

    Following is criteria to check recency
    https://uktrade.atlassian.net/wiki/spaces/Great/pages/2139750605/Ranking+mechanism+-+CMS+UI+for+weighting+and+threshold+changes

    <= Recency 3 months
    <= Recency 6 months
    <= Recency 9 months
    <= Recency 12 months
    <= Recency 15 months
    <= Recency 18 months
    <= Recency 21 months
    <= Recency 24 months and > 24 months
    """

    # month list of 3 to 24 years in 3 month interval
    recency_months = range(3, 25, 3)

    for index, month_number in enumerate(recency_months):
        if month_number >= month:
            return month_number
        if month_number < month < recency_months[index + 1]:
            return recency_months[index + 1]
        if month > recency_months[-1]:
            return recency_months[-1]
