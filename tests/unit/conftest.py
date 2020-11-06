from unittest import mock
import pytest

from tests.unit.core.factories import (
    CuratedListPageFactory,
    LessonPlaceholderPageFactory,
    ListPageFactory,
    TopicPageFactory,
)
from tests.unit.learn import factories as learn_factories
from captcha.client import RecaptchaResponse


@pytest.mark.django_db(transaction=True)
@pytest.fixture
def curated_list_pages_with_lessons(domestic_homepage):
    list_page = ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    clp_a = CuratedListPageFactory(parent=list_page, title='Lesson topic A', slug='topic-a',)
    topic_for_clp_a = TopicPageFactory(parent=clp_a, title='Some title')
    lesson_a1 = learn_factories.LessonPageFactory(
        parent=topic_for_clp_a,
        title='Lesson A1',
        slug='lesson-a1',
    )
    LessonPlaceholderPageFactory(parent=topic_for_clp_a, title='Placeholder One')
    lesson_a2 = learn_factories.LessonPageFactory(
        parent=topic_for_clp_a,
        title='Lesson A2',
        slug='lesson-a2',
    )

    clp_b = CuratedListPageFactory(parent=list_page, title='Lesson topic b', slug='topic-b',)
    topic_for_clp_b = TopicPageFactory(parent=clp_b, title='Some title b')
    lesson_b1 = learn_factories.LessonPageFactory(
        parent=topic_for_clp_b,
        title='Lesson b1',
        slug='lesson-b1',
    )

    return [(clp_a, [lesson_a1, lesson_a2]), (clp_b, [lesson_b1])]


@pytest.fixture(autouse=True)
def mock_captcha_clean():
    patch = mock.patch('captcha.fields.ReCaptchaField.clean', return_value='PASS')
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def captcha_stub():
    stub = mock.patch('captcha.fields.client.submit')
    stub.return_value = RecaptchaResponse(is_valid=False, extra_data={'score': 1.0})
    stub.start()
    yield 'PASSED'
    stub.stop()
