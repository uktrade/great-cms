from random import choice

import pytest

from tests.browser.common_selectors import (
    DashboardReadingProgress,
    TopicLessonListing,
    LessonPage
)
from tests.browser.util import (
    attach_jpg_screenshot,
    should_see_all_elements,
    should_not_see_errors,
    selenium_action
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


def test_can_mark_lesson_as_read(
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

    mark_as_read_link = browser.find_element(
        by=LessonPage.MARK_AS_READ.by,
        value=LessonPage.MARK_AS_READ.selector,
    )

    with selenium_action(browser, f'Failed to mark lesson as read'):
        mark_as_read_link.click()

    attach_jpg_screenshot(browser, 'topic listing with read lesson')
    should_see_all_elements(browser, TopicLessonListing)

    lesson_link = browser.find_element_by_id(f'lesson-{topic_a_lessons[0].slug}')
    error = f'Expected lesson: "{topic_a_lessons[0].title}" is not marked as read!'
    assert ' [is read]' in lesson_link.text, error
