import pytest

from tests.unit.core.factories import CuratedListPageFactory
from tests.unit.learn import factories
from core.context import get_context_provider


@pytest.mark.django_db
def test_lesson_page_context_provider(rf, domestic_homepage, user):
    request = rf.get('/')
    request.user = user
    CuratedListPageFactory(slug='topic-one', parent=domestic_homepage)
    CuratedListPageFactory(slug='topic-two', parent=domestic_homepage)
    topic = CuratedListPageFactory(slug='topic-three', parent=domestic_homepage)
    page = factories.LessonPageFactory(slug='lesson-one', parent=topic)

    provider = get_context_provider(request=request, page=page)

    context = provider.get_context_data(request=request, page=page)

    assert context['topics'].count() == 3
    assert context['country_choices']
