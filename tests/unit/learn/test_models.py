import pytest

from tests.unit.learn import factories


@pytest.mark.django_db
def test_topic_view(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    factories.LessonPageFactory(parent=topic)

    response = client.get(topic.url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_lesson_page_products(client, domestic_homepage, domestic_site, user):
    client.force_login(user)

    # given the user has not read a lesson
    topic = factories.TopicPageFactory(parent=domestic_homepage)
    lesson = factories.LessonPageFactory(parent=topic)

    response = client.get(lesson.url, {'products_label': 'some_product'})

    # then the progress is unaffected
    assert response.status_code == 200
