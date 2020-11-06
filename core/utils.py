def get_all_lessons(module) -> list:
    """
    Helper function to get all lessons of a module (CuratedListPage) that have
    TopicPages between the module and the lessons.

    @returns: List of DetailPage objects (lessons)
    """
    from core.models import DetailPage, TopicPage
    return [
        lesson for lesson in
        DetailPage.objects.live().specific().descendant_of(module)
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
        self.module = self.page.get_parent().get_parent()
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


def create_filter_dict(product_code=None, target_area=None):
    """
     Helper function to create filter dict based on product and target area

    @param product_code: HS code ( HS6, HS4 or HS2)
    @param target_area: country_iso or region
    @return: dict
    """

    result = dict()
    if product_code:
        result['hs_code_tags__name'] = product_code
    if target_area:
        result['country_code_tags__name'] = target_area
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

    filter_args, unique_hs_codes = [], []
    # Removing null item then added None to filter against product_code crieatria
    region_list = [i for i in [country, region] if i] + [None]
    is_region = any(region_list)

    if hs_code:
        hs_codes = [hs_code[i] for i in [slice(6), slice(4), slice(2)]]
        # Removing identical item while keeping order of item
        unique_hs_codes = sorted(set(hs_codes), key=hs_codes.index)

    if unique_hs_codes and is_region:
        filter_args = [
            create_filter_dict(product_code=code, target_area=area)
            for code in unique_hs_codes
            for area in region_list
        ]
    elif unique_hs_codes:
        filter_args = [
            create_filter_dict(product_code=code, target_area=None)
            for code in unique_hs_codes
        ]
    if is_region:
        filter_args = filter_args + [
            create_filter_dict(product_code=None, target_area=area)
            for area in region_list
        ]

    return [i for i in filter_args if i]
