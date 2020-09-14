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
        self.module_pages = self.get_module_lessons()
        self.next_lesson = self.get_next_lesson()

    def get_page_topic(self):
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
        return len(self.module_pages)

    def get_module_lessons(self):
        return [
            page for topic in self.module.topics
            for page in topic.value['pages']
            if page.live
        ]

    def get_topic_page_pairs(self):
        return [
            (topic.value['title'], page)
            for topic in self.module.topics
            for page in topic.value['pages']
            if page.live
        ]

    def get_next_lesson(self):
        for i, item in enumerate(self.get_topic_page_pairs()):
            if self.page.id == item[1].id:
                try:
                    return self.get_topic_page_pairs()[i + 1]
                except IndexError:
                    return
