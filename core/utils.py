def get_all_lessons(module):
    """
    Helper function to get all lesson of a module
    @return: list of lesson objects
    """
    lessons = [
        page
        for topic in module.specific.topics
        for page in topic.value["pages"]
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
            for page in topic.value["pages"]:
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


def get_selected_personalised_choices(request):
    commodity_code, country, region = None, None, None

    if not hasattr(request.user, "export_plan"):
        return

    export_commodity_codes = request.user.export_plan.get("export_commodity_codes")
    for item in export_commodity_codes:
        commodity_code = item["commodity_code"].lower()

    export_countries = request.user.export_plan.get("export_countries")
    for item in export_countries:
        country = item["country_iso2_code"].lower()
        region = item["region"].lower()

    return commodity_code, country, region


def create_filter_dict(product_code=None, target_area=None):
    result = dict()
    if product_code:
        # TODO: change tag filed based on case study model field
        result["product_tags__name__exact"] = product_code
    if target_area:
        # TODO: change tag filed based on case study model field
        result["country_tags__name__exact"] = target_area

    return result if result else None


def get_personalised_case_study_filter_dict(
    product_code=None, country=None, region=None
):
    """
    Helper function to generate filter criteria for ORM query to get
    Personalised Case study

    @param product_code: HS code (hs6, hs4 and hs2)
    @param country: country iso2 code
    @param region: region ( for example 'Asia')
    @return: filter dict
    """
    filter_args, unique_hs_codes = [], []
    # Removing null item then added None to filter against product_code crieatria
    region_list = [i for i in [country, region] if i] + [None]
    is_region = any(region_list)

    if product_code:
        hs_codes = [product_code[i] for i in [slice(6), slice(4), slice(2)]]
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
    elif is_region:
        filter_args = [
            create_filter_dict(product_code=None, target_area=area)
            for area in region_list
        ]

    return [i for i in filter_args if i]
