from wagtail.tests.utils import WagtailPageTests

from domestic.models import DomesticHomePage
from learn.models import TopicPage


class TopicPageTests(WagtailPageTests):

    def test_can_be_created_under_root(self):
        self.assertAllowedParentPageTypes(TopicPage, {DomesticHomePage})
