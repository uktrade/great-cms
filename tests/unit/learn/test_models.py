import pytest

from tests.unit.core.factories import CuratedListPageFactory
from tests.unit.learn import factories


@pytest.mark.django_db
def test_topic_view(client, domestic_homepage, user, domestic_site, mock_get_user_profile):
    # given the user has not read a lesson
    client.force_login(user)
    topic = CuratedListPageFactory(parent=domestic_homepage)
    factories.LessonPageFactory(parent=topic)

    response = client.get(topic.url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_lesson_page_products(
    client, domestic_homepage, domestic_site, user, mock_export_plan_detail_list, mock_get_user_profile
):
    client.force_login(user)

    # given the user has not read a lesson
    topic = CuratedListPageFactory(parent=domestic_homepage)
    lesson = factories.LessonPageFactory(parent=topic)

    response = client.get(lesson.url, {'products_label': 'some_product'})

    # then the progress is unaffected
    assert response.status_code == 200
