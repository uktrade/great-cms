import pytest
from wagtail.tests.utils import WagtailPageTests

from domestic.models import DomesticHomePage
from learn.models import LearnPage, LessonPage, TopicPage
from tests.unit.learn import factories


class TopicPageTests(WagtailPageTests):

    def test_can_be_created_under_root(self):
        self.assertAllowedParentPageTypes(TopicPage, {DomesticHomePage})

    def test_can_create_child_lesson(self):
        self.assertAllowedSubpageTypes(TopicPage, {LessonPage})


class LessonPageTests(WagtailPageTests):

    def test_can_be_created_under_topic(self):
        self.assertCanCreateAt(TopicPage, LessonPage)


class LearnPageTests():

    def test_can_be_created_under_root(self):
        self.assertAllowedParentPageTypes(DomesticHomePage, LearnPage)


@pytest.mark.django_db
def test_topic_view(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    factories.LessonPageFactory(parent=topic)

    response = client.get(topic.url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_learn_page_view(client, domestic_homepage, user, domestic_site):
    page = factories.LearnPageFactory(parent=domestic_homepage)

    response = client.get(page.url)
    assert response.status_code == 200
