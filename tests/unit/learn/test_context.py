from tests.unit.learn import factories
from core.context import get_context_provider


def test_lesson_page_context_provider(rf, domestic_homepage):
    request = rf.get('/')
    factories.TopicPageFactory(slug='topic-one', parent=domestic_homepage)
    factories.TopicPageFactory(slug='topic-two', parent=domestic_homepage)
    topic = factories.TopicPageFactory(slug='topic-three', parent=domestic_homepage)
    page = factories.LessonPageFactory(slug='lesson-one', parent=topic)

    provider = get_context_provider(request=request, page=page)

    context = provider.get_context_data(request=request, page=page)

    assert context['topics'].count() == 3
    assert context['country_choices']
