import pytest
from django.http import HttpRequest

from core.utils import (  # get_personalised_case_study_orm_filter_args,
    PageTopicHelper,
    choices_to_key_value,
    get_all_lessons,
    get_first_lesson,
    get_personalised_choices,
)
from directory_constants.choices import MARKET_ROUTE_CHOICES
from tests.unit.core import factories


@pytest.mark.django_db
def test_lesson_module(domestic_homepage):
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    curated_list_page = factories.CuratedListPageFactory(
        parent=list_page,
    )
    topic_one = factories.TopicPageFactory(title='Topic 1', parent=curated_list_page)
    topic_two = factories.TopicPageFactory(title='Topic 2', parent=curated_list_page)
    detail_page_1 = factories.DetailPageFactory(slug='detail-page-1', parent=topic_one)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-2', parent=topic_one)
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-3', parent=topic_two)
    detail_page_4__not_configured_in_topic_so_should_be_skipped = factories.DetailPageFactory(
        slug='detail-page-3', parent=curated_list_page  # This will become impossible but worth testing for now
    )
    assert detail_page_4__not_configured_in_topic_so_should_be_skipped.get_parent() == curated_list_page

    pt_1 = PageTopicHelper(detail_page_1)

    assert pt_1.total_module_lessons() == 3
    assert pt_1.total_module_topics() == 2
    assert pt_1.get_next_lesson() == detail_page_2

    # Last lesson of topic should have following topic's first lesson as next lesson
    pt_2 = PageTopicHelper(detail_page_2)
    assert pt_2.get_next_lesson() == detail_page_3

    pt_3 = PageTopicHelper(detail_page_3)

    # last page of module should have None as next lesson
    assert pt_3.get_next_lesson() is None


@pytest.mark.django_db
def test_lesson_module__get_first_lesson__unhappy_path(domestic_homepage):
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    empty_module = factories.CuratedListPageFactory(
        parent=list_page,
    )
    assert get_first_lesson(empty_module) is None


@pytest.mark.django_db
def test_multiple_modules(domestic_homepage, client, user):
    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    module_1 = factories.CuratedListPageFactory(
        title='Module 1',
        parent=list_page,
    )
    module_2 = factories.CuratedListPageFactory(
        title='Module 2',
        parent=list_page,
    )

    topic_1 = factories.TopicPageFactory(title='Topic 1', parent=module_1)
    topic_2 = factories.TopicPageFactory(title='Topic 2', parent=module_1)
    topic_3 = factories.TopicPageFactory(title='Topic 2', parent=module_2)

    detail_page_1 = factories.DetailPageFactory(slug='detail-page-11', parent=topic_1)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-12', parent=topic_1)
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-13', parent=topic_2)
    detail_page_4 = factories.DetailPageFactory(slug='detail-page-24', parent=topic_3)

    pt_1 = PageTopicHelper(detail_page_1)
    pt_2 = PageTopicHelper(detail_page_2)
    pt_3 = PageTopicHelper(detail_page_3)

    assert get_first_lesson(module_1) == detail_page_1
    assert get_first_lesson(module_2) == detail_page_4

    assert len(get_all_lessons(module_1)) == 3
    assert len(get_all_lessons(module_2)) == 1

    assert pt_1.get_next_lesson() == detail_page_2
    assert pt_2.get_next_lesson() == detail_page_3
    # last page of module should have None as next lesson
    assert pt_3.get_next_lesson() is None

    client.force_login(user)

    request = HttpRequest()
    request.user = user

    page1_response = detail_page_1.serve(request)
    page2_response = detail_page_2.serve(request)
    page3_response = detail_page_3.serve(request)
    page4_response = detail_page_4.serve(request)

    assert page1_response.context_data['next_lesson'].specific == detail_page_2
    assert page1_response.context_data['current_module'].specific == module_1
    assert page1_response.context_data.get('next_module') is None  # only present for final lesson in module

    assert page2_response.context_data['next_lesson'].specific == detail_page_3
    assert page2_response.context_data['current_module'].specific == module_1
    assert page2_response.context_data.get('next_module') is None  # only present for final lesson in module

    assert page3_response.context_data['next_lesson'].specific == detail_page_4
    assert page3_response.context_data['current_module'].specific == module_1
    assert page3_response.context_data['next_module'].specific == module_2

    assert page4_response.context_data.get('next_lesson') is None
    assert page4_response.context_data['current_module'] == module_2
    assert page4_response.context_data.get('next_module') is None  # no next module, even though final lesson


@pytest.mark.django_db
def test_placeholders_do_not_get_counted(domestic_homepage, client, user):
    # Almost literally the same test as above, but with some placeholder blocks
    # mixed in to show that they don't affect lesson counts or 'next' lessons

    list_page = factories.ListPageFactory(parent=domestic_homepage, record_read_progress=True)
    module_1 = factories.CuratedListPageFactory(
        title='Module 1',
        parent=list_page,
    )
    module_2 = factories.CuratedListPageFactory(
        title='Module 2',
        parent=list_page,
    )
    topic_1 = factories.TopicPageFactory(title='Topic 1', parent=module_1)
    topic_2 = factories.TopicPageFactory(title='Topic 2', parent=module_1)
    topic_3 = factories.TopicPageFactory(title='Topic 2', parent=module_2)

    # Topic One's children
    detail_page_1 = factories.DetailPageFactory(slug='detail-page-11', parent=topic_1)
    factories.LessonPlaceholderPageFactory(title='Topic One: Placeholder One', parent=topic_1)
    detail_page_2 = factories.DetailPageFactory(slug='detail-page-12', parent=topic_1)
    factories.LessonPlaceholderPageFactory(title='Topic One: Placeholder Two', parent=topic_1)

    # Topic Two's children
    detail_page_3 = factories.DetailPageFactory(slug='detail-page-13', parent=topic_2)
    factories.LessonPlaceholderPageFactory(title='Topic Two: Placeholder One', parent=topic_2)
    factories.LessonPlaceholderPageFactory(title='Topic Two: Placeholder Two', parent=topic_2)

    factories.LessonPlaceholderPageFactory(title='Topic Two: Placeholder Three', parent=topic_2)

    # Topic Three's children
    factories.LessonPlaceholderPageFactory(title='Topic Three: Placeholder one', parent=topic_3)
    detail_page_4 = factories.DetailPageFactory(slug='detail-page-24', parent=topic_3)
    factories.LessonPlaceholderPageFactory(title='Topic Three: Placeholder Two', parent=topic_3)

    pt_1 = PageTopicHelper(detail_page_1)
    pt_2 = PageTopicHelper(detail_page_2)
    pt_3 = PageTopicHelper(detail_page_3)

    assert get_first_lesson(module_1) == detail_page_1
    assert get_first_lesson(module_2) == detail_page_4  # placeholder skipped

    assert len(get_all_lessons(module_1)) == 3  # placeholders skipped
    assert len(get_all_lessons(module_2)) == 1  # placeholders skipped

    assert pt_1.get_next_lesson() == detail_page_2
    assert pt_2.get_next_lesson() == detail_page_3
    # last page of module should have None as next lesson
    assert pt_3.get_next_lesson() is None

    client.force_login(user)

    request = HttpRequest()
    request.user = user

    page1_response = detail_page_1.serve(request)
    page2_response = detail_page_2.serve(request)
    page3_response = detail_page_3.serve(request)
    page4_response = detail_page_4.serve(request)

    assert page1_response.context_data['next_lesson'].specific == detail_page_2
    assert page1_response.context_data['current_module'].specific == module_1
    assert page1_response.context_data.get('next_module') is None  # only present for final lesson in module

    assert page2_response.context_data['next_lesson'].specific == detail_page_3
    assert page2_response.context_data['current_module'].specific == module_1
    assert page2_response.context_data.get('next_module') is None  # only present for final lesson in module

    assert page3_response.context_data['next_lesson'].specific == detail_page_4
    assert page3_response.context_data['current_module'].specific == module_1
    assert page3_response.context_data['next_module'].specific == module_2

    assert page4_response.context_data.get('next_lesson') is None
    assert page4_response.context_data['current_module'] == module_2
    assert page4_response.context_data.get('next_module') is None  # no next module, even though final lesson


@pytest.mark.django_db
def test_selected_personalised_choices(rf, user, mock_get_user_data, mock_trading_blocs):
    request = rf.get('/')
    request.user = user
    commodity_codes, countries, regions, blocs = get_personalised_choices(user)

    assert commodity_codes == ['111111', '666666']
    assert countries == ['Germany']
    assert regions == ['Europe']
    assert 'European Economic Area (EEA)' in blocs
    assert 'European Union (EU)' in blocs


@pytest.mark.django_db
def test_selected_personalised_choices_no_user():
    commodity_codes, countries, regions, blocs = get_personalised_choices(None)

    assert commodity_codes == []
    assert countries == []
    assert regions == []


def test_tuple_to_key_value_dict():
    key_value_dict = [{'value': key, 'label': label} for key, label in MARKET_ROUTE_CHOICES]
    assert choices_to_key_value(MARKET_ROUTE_CHOICES) == key_value_dict
