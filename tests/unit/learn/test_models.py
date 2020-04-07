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


@pytest.mark.django_db
def test_lesson_page_can_mark_as_read(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    lesson = factories.LessonPageFactory(parent=topic)

    client.get(lesson.url)

    # then the progress is saved
    read_hit = lesson.read_hits.get()
    assert read_hit.sso_id == str(user.pk)
    assert read_hit.topic == topic


@pytest.mark.django_db
def test_lesson_page_anon_user_not_marked_as_read(client, domestic_homepage, domestic_site):
    # given the user has not read a lesson
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    lesson = factories.LessonPageFactory(
        parent=topic,
        generic_content='some content',
    )

    client.get(lesson.url)

    # then the progress is unaffected
    assert lesson.read_hits.count() == 0


@pytest.mark.django_db
def test_lesson_page_products(client, domestic_homepage, domestic_site):
    # given the user has not read a lesson
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    lesson = factories.LessonPageFactory(parent=topic)

    response = client.get(lesson.url, {'products_label': 'some_product'})

    # then the progress is unaffected
    assert response.status_code == 200


@pytest.mark.django_db
def test_lesson_page_user_has_expertise(client, domestic_homepage, user, domestic_site, mock_get_company_profile):
    mock_get_company_profile.return_value = {
        'expertise_countries': ['cz'],
        'expertise_industries': [],
    }

    # given the user has not read a lesson
    client.force_login(user)
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    lesson = factories.LessonPageFactory(parent=topic)

    client.get(lesson.url)


@pytest.mark.django_db
def test_lesson_page_has_next(client, domestic_homepage, domestic_site):
    # given the user has not read a lesson
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    lesson = factories.LessonPageFactory(
        parent=topic,
        generic_content='some content',
        slug='some-lesson'
    )
    factories.LessonPageFactory(
        parent=topic,
        generic_content='some other content',
        slug='some-other-lesson'
    )

    client.get(lesson.url)

    # then the progress is unaffected
    assert lesson.read_hits.count() == 0
