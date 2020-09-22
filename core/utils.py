def get_all_lessons(module):
    """
    Helper function to get all lesson of a module
    @return: list of lesson objects
    """
    lessons = [page for topic in module.specific.topics for page in topic.value['pages'] if page.live]
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
        # the `topics` StreamField, so we have to find them this way, rather than via the ORM
        for topic in self.module.topics:
            for page in topic.value['pages']:
                if self.page.id == page.id:
                    return topic.value

    def get_module_topics(self):
        return [topic for topic in self.module.topics]

    @property
    def total_module_topics(self):
        return len(self.get_module_topics())

    @property
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
