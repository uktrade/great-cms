from random import choice

import pytest

from tests.browser.common_selectors import (
    DashboardReadingProgress,
    LessonPage,
    TopicLessonListing,
)
from tests.browser.util import (
    attach_jpg_screenshot,
    selenium_action,
    should_not_see_errors,
    should_see_all_elements,
)

pytestmark = [
    pytest.mark.browser,
    pytest.mark.lesson,
]


def test_can_view_lessons_from_different_topics(
    mock_dashboard_profile_events_opportunities,
    mock_export_plan_requests,
    topics_with_lessons,
    server_user_browser_dashboard,
):
    live_server, user, browser = server_user_browser_dashboard
    should_not_see_errors(browser)

    topic_a, topic_a_lessons = topics_with_lessons[0]
    topic_b, topic_b_lessons = topics_with_lessons[1]

    browser.get(f'{live_server.url}/dashboard/')
    attach_jpg_screenshot(browser, 'dashboard with lessons')
    should_see_all_elements(browser, DashboardReadingProgress)

    browser.get(f'{live_server.url}/{topic_a.slug}/')
    attach_jpg_screenshot(browser, 'topic_a')
    should_see_all_elements(browser, TopicLessonListing)
    browser.get(f'{live_server.url}/{topic_a.slug}/{topic_a_lessons[0].slug}/')
    attach_jpg_screenshot(browser, 'lesson_a1')
    should_see_all_elements(browser, LessonPage)
    browser.get(f'{live_server.url}/{topic_a.slug}/{topic_a_lessons[1].slug}/')
    attach_jpg_screenshot(browser, 'lesson_a2')
    should_see_all_elements(browser, LessonPage)

    browser.get(f'{live_server.url}/{topic_b.slug}/')
    attach_jpg_screenshot(browser, 'topic_b')
    should_see_all_elements(browser, TopicLessonListing)
    browser.get(f'{live_server.url}/{topic_b.slug}/{topic_b_lessons[0].slug}/')
    attach_jpg_screenshot(browser, 'lesson_b1')
    should_see_all_elements(browser, LessonPage)
    browser.get(f'{live_server.url}/{topic_b.slug}/{topic_b_lessons[1].slug}/')
    attach_jpg_screenshot(browser, 'lesson_b2')
    should_see_all_elements(browser, LessonPage)


def test_can_navigate_from_topic_to_lesson(
    mock_dashboard_profile_events_opportunities,
    mock_export_plan_requests,
    topics_with_lessons,
    server_user_browser_dashboard,
):
    live_server, user, browser = server_user_browser_dashboard
    should_not_see_errors(browser)

    topic_a, topic_a_lessons = topics_with_lessons[0]

    browser.get(f'{live_server.url}/{topic_a.slug}/')
    attach_jpg_screenshot(browser, 'topic_a')

    lesson_links = browser.find_elements(
        by=TopicLessonListing.LESSON_LINKS.by,
        value=TopicLessonListing.LESSON_LINKS.selector,
    )
    lesson_link = choice(lesson_links)

    with selenium_action(browser, f'Failed to view lesson: {lesson_link.text}'):
        lesson_link.click()

    attach_jpg_screenshot(browser, 'random_lesson')
    should_see_all_elements(browser, LessonPage)


def test_can_mark_lesson_as_read_and_check_read_progress_on_dashboard_page(
    mock_dashboard_profile_events_opportunities,
    mock_export_plan_requests,
    topics_with_lessons,
    server_user_browser_dashboard,
):
    live_server, user, browser = server_user_browser_dashboard
    should_not_see_errors(browser)

    topic_a, topic_a_lessons = topics_with_lessons[0]

    browser.get(f'{live_server.url}/{topic_a.slug}/{topic_a_lessons[0].slug}/')
    attach_jpg_screenshot(browser, 'lesson_a1')
    should_see_all_elements(browser, LessonPage)

    browser.get(f'{live_server.url}/dashboard/')
    attach_jpg_screenshot(browser, 'dashboard with read lesson')
    should_see_all_elements(browser, DashboardReadingProgress)

    topic_read_count = browser.find_element_by_id(f'topics-read-count-lesson-{topic_a.slug}')
    no_of_lessons = topic_read_count.get_property('max')
    no_of_read_lessons = topic_read_count.get_property('value')
    assert no_of_lessons == len(topic_a_lessons)
    assert no_of_read_lessons == 1
