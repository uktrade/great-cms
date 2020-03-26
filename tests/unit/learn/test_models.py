import pytest
from wagtail.tests.utils import WagtailPageTests

from domestic.models import DomesticHomePage
from learn.models import TopicPage, LessonPage
from tests.unit.learn import factories


class TopicPageTests(WagtailPageTests):

    def test_can_be_created_under_root(self):
        self.assertAllowedParentPageTypes(TopicPage, {DomesticHomePage})

    def test_can_create_child_lesson(self):
        self.assertAllowedSubpageTypes(TopicPage, {LessonPage})


class LessonPageTests(WagtailPageTests):

    def test_can_be_created_under_topic(self):
        self.assertCanCreateAt(TopicPage, LessonPage)


@pytest.mark.django_db
def test_lesson_page_can_mark_as_read(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    lesson = factories.LessonPageFactory(parent=topic)

    response = client.get(lesson.url)
    assert response.context_data['is_read'] is False

    # when the user marks the lesson as read
    response = client.post(lesson.url + lesson.reverse_subpage('mark-as-read'))

    assert response.status_code == 302
    assert response.url == topic.get_url()

    # then the progress is saved
    read_hit = lesson.read_hits.get()
    assert read_hit.sso_id == str(user.pk)
    assert read_hit.topic == topic

    # and the progress is retrieved
    response = client.get(lesson.url)
    assert response.context_data['is_read'] is True


@pytest.mark.django_db
def test_topic_view(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    factories.LessonPageFactory(parent=topic)

    response = client.get(topic.url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_learn_landing_page_view(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    factories.LessonPageFactory(parent=topic)

    response = client.get(topic.url)
    assert response.status_code == 200
