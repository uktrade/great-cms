def get_all_lessons(module):
    """
    Helper function to get all lesson of a module
    @return: list of lesson objects
    """
    lessons = [
        page
        for topic in module.specific.topics
        for page in topic.value['pages']
        if page.live
    ]
    if lessons:
        return lessons


def get_first_lesson(module):
    """
    Helper function to get first lesson of a module
    @return: lesson object
    """
    lessons = get_all_lessons(module)
    if lessons:
        return lessons[0]


class PageTopic:
    """
    Utility class for Page's topic. Helper class gather all info regarding topic specific for relevant page.
    For example given page it calculate next lesson of topic.

    """

    def __init__(self, page):
        self.page = page
        self.module = page.get_parent().specific
        self.page_topic = self.get_page_topic()
        self.module_topics = self.get_module_topics()
        self.module_lessons = get_all_lessons(self.module)

    def get_page_topic(self):
        # the `topics` StreamField, so we have to find them this way, rather than via the ORM
        # The user-facing relationship between lessons and their topics exists only through
        for topic in self.module.topics:
            for page in topic.value['pages']:
                if self.page.id == page.id:
                    return topic.value

    def get_module_topics(self):
        return [topic for topic in self.module.topics]

    def total_module_topics(self):
        return len(self.get_module_topics())

    def total_module_lessons(self):
        return len(self.module_lessons)

    def get_next_lesson(self):
        lessons = get_all_lessons(self.module)
        if not lessons:
            return
        for i, item in enumerate(lessons):
            if self.page.id == item.id:
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
