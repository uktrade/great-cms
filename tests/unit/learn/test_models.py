from wagtail.tests.utils import WagtailPageTests

from domestic.models import DomesticHomePage
from learn.models import TopicPage, LessonPage


class TopicPageTests(WagtailPageTests):

    def test_can_be_created_under_root(self):
        self.assertAllowedParentPageTypes(TopicPage, {DomesticHomePage})

    def test_can_create_child_lesson(self):
        self.assertAllowedSubpageTypes(TopicPage, {LessonPage})


class LessonPageTests(WagtailPageTests):

    def test_can_be_created_under_topic(self):
        self.assertAllowedParentPageTypes(LessonPage, {TopicPage})
