import pytest

from tests.unit.core.factories import (
    CuratedListPageFactory,
    DetailPageFactory,
    ListPageFactory,
    TopicPageFactory,
    TourFactory,
)
from tests.unit.learn import factories


@pytest.mark.django_db
def test_topic_view(client, domestic_homepage, user, domestic_site):
    # given the user has not read a lesson
    client.force_login(user)
    topic = CuratedListPageFactory(parent=domestic_homepage)
    factories.LessonPageFactory(parent=topic)

    response = client.get(topic.url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_lesson_page_products(client, domestic_homepage, domestic_site, user, patch_export_plan):
    client.force_login(user)

    # given the user has not read a lesson
    topic = CuratedListPageFactory(parent=domestic_homepage)
    lesson = factories.LessonPageFactory(parent=topic)

    response = client.get(lesson.url, {'products_label': 'some_product'})

    # then the progress is unaffected
    assert response.status_code == 200


@pytest.mark.django_db
def test_tour_page(client, domestic_homepage, domestic_site, user):
    client.force_login(user)

    list_page = ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    curated_list_page = CuratedListPageFactory(parent=list_page)
    topic_page = TopicPageFactory(parent=curated_list_page)
    detail_page = DetailPageFactory(parent=topic_page)

    tour = TourFactory(page=detail_page, title='Tour title')
    assert tour.__str__() == 'Detail page'

    response = client.get(detail_page.url)
    assert response.status_code == 200
