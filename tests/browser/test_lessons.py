# -*- coding: utf-8 -*-
from random import choice
from typing import List

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

import allure
from pytest_django.live_server_helper import LiveServer
from tests.browser.common_selectors import (
    DashboardReadingProgress,
    LessonPage,
    TopicLessonListing,
)
from tests.browser.steps import should_see_all_elements, visit_page
from tests.browser.util import attach_jpg_screenshot, selenium_action
from tests.unit.core.factories import DetailPageFactory, ListPageFactory

pytestmark = [
    pytest.mark.browser,
    pytest.mark.lesson,
]


@allure.step('Visit lesson listing page: {page_name}')
def visit_lesson_listing_page(live_server: LiveServer, browser: WebDriver, page_name: str, endpoint: str):
    visit_page(live_server, browser, '', page_name, endpoint=endpoint)
    should_see_all_elements(browser, TopicLessonListing)


@allure.step('Visit {page_name} page')
def visit_lesson_page(live_server: LiveServer, browser: WebDriver, page_name: str, endpoint: str):
    visit_page(live_server, browser, '', page_name, endpoint=endpoint)
    should_see_all_elements(browser, LessonPage)


@allure.step('Open random lesson on lesson listing page')
def open_random_lesson(browser: WebDriver):
    lesson_links = browser.find_elements(
        by=TopicLessonListing.LESSON_LINKS.by, value=TopicLessonListing.LESSON_LINKS.selector,
    )
    lesson_link = choice(lesson_links)

    with selenium_action(browser, f'Failed to view lesson: {lesson_link.text}'):
        lesson_link.click()

    attach_jpg_screenshot(browser, 'Lesson page')


@allure.step('Check topics reading progress')
def check_topic_read_progress(browser: WebDriver, topic: ListPageFactory, lessons: List[DetailPageFactory]):
    attach_jpg_screenshot(browser, 'Topics reading progress', selector=DashboardReadingProgress.YOUR_PROGRESS_CARD)
    list_page = topic.get_parent()

    topic_read_count = browser.find_element_by_id(f'topics-read-count-{list_page.slug}')
    no_of_lessons = topic_read_count.get_property('max')
    no_of_read_lessons = topic_read_count.get_property('value')
    assert no_of_lessons == len(lessons)
    assert no_of_read_lessons == 1


def test_can_view_lessons_from_different_topics(
    mock_dashboard_profile_events_opportunities,
    mock_export_plan_requests,
    topics_with_lessons,
    server_user_browser_dashboard,
):
    live_server, user, browser = server_user_browser_dashboard
    topic_a, topic_a_lessons = topics_with_lessons[0]
    topic_b, topic_b_lessons = topics_with_lessons[1]

    visit_page(live_server, browser, 'core:dashboard', 'Dashboard')
    should_see_all_elements(browser, DashboardReadingProgress)

    visit_lesson_listing_page(live_server, browser, 'Topic A', topic_a.slug)
    visit_lesson_page(live_server, browser, 'Topic A - Lesson A1', f'/{topic_a.slug}/{topic_a_lessons[0].slug}/')
    visit_lesson_page(live_server, browser, 'Topic A - Lesson A2', f'/{topic_a.slug}/{topic_a_lessons[1].slug}/')

    visit_lesson_listing_page(live_server, browser, 'Topic B', topic_b.slug)
    visit_lesson_page(live_server, browser, 'Topic B - Lesson B1', f'/{topic_b.slug}/{topic_b_lessons[0].slug}/')
    visit_lesson_page(live_server, browser, 'Topic B - Lesson B2', f'/{topic_b.slug}/{topic_b_lessons[1].slug}/')


def test_can_navigate_from_topic_to_lesson(
    mock_dashboard_profile_events_opportunities,
    mock_export_plan_requests,
    topics_with_lessons,
    server_user_browser_dashboard,
):
    live_server, user, browser = server_user_browser_dashboard
    topic_a, topic_a_lessons = topics_with_lessons[0]
    visit_lesson_listing_page(live_server, browser, 'Topic A', topic_a.slug)

    open_random_lesson(browser)

    should_see_all_elements(browser, LessonPage)


def test_can_mark_lesson_as_read_and_check_read_progress_on_dashboard_page(
    mock_dashboard_profile_events_opportunities,
    mock_export_plan_requests,
    topics_with_lessons,
    server_user_browser_dashboard,
):
    live_server, user, browser = server_user_browser_dashboard
    topic_a, topic_a_lessons = topics_with_lessons[0]

    visit_lesson_page(live_server, browser, 'Topic A - Lesson A1', topic_a_lessons[0].url)

    visit_page(live_server, browser, 'core:dashboard', 'Dashboard')
    should_see_all_elements(browser, DashboardReadingProgress)

    check_topic_read_progress(browser, topic_a, topic_a_lessons)
