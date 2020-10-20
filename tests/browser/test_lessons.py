# -*- coding: utf-8 -*-
from random import choice
from typing import List
from unittest import mock

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

import allure
from pytest_django.live_server_helper import LiveServer
from tests.browser.common_selectors import (
    DashboardReadingProgress,
    LessonPage,
    TopicLessonListing,
)
from tests.browser.steps import should_see_all_elements, should_not_see_any_element, visit_page
from tests.browser.util import attach_jpg_screenshot, selenium_action
from tests.unit.core.factories import DetailPageFactory, ListPageFactory, CuratedListPageFactory
from core import constants
from sso import helpers as sso_helpers

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
    count_element = browser.find_element_by_css_selector('#your-progress-card .topics-read-text')
    count_text = count_element.text
    assert count_text == '1/2 complete'


def test_can_view_lessons_from_different_topics(
    mock_get_lessons_completed,
    mock_dashboard_profile_events_opportunities,
    mock_export_plan_requests,
    curated_list_pages_with_lessons_and_placeholders,
    server_user_browser_dashboard,
):

    live_server, user, browser = server_user_browser_dashboard
    clp_a, clp_a_lessons = curated_list_pages_with_lessons_and_placeholders[0]
    clp_b, clp_b_lessons = curated_list_pages_with_lessons_and_placeholders[1]

    visit_page(live_server, browser, None, 'Dashboard', endpoint=constants.DASHBOARD_URL)

    visit_lesson_listing_page(live_server, browser, 'Topic A', clp_a.url)
    visit_lesson_page(live_server, browser, 'Topic A - Lesson A1', clp_a_lessons[0].url)
    visit_lesson_page(live_server, browser, 'Topic A - Lesson A2', clp_a_lessons[1].url)

    visit_lesson_listing_page(live_server, browser, 'Topic B', clp_b.url)
    visit_lesson_page(live_server, browser, 'Topic B - Lesson B1', clp_b_lessons[0].url)
    visit_lesson_page(live_server, browser, 'Topic B - Lesson B2', clp_b_lessons[1].url)


@mock.patch.object(sso_helpers, 'get_lesson_completed')
def test_can_mark_lesson_as_read_and_check_read_progress_on_dashboard_page(
    mock_get_lesson_completed,
    mock_dashboard_profile_events_opportunities,
    mock_export_plan_requests,
    curated_list_pages_with_lessons_and_placeholders,
    server_user_browser_dashboard,
    domestic_homepage,
):
    live_server, user, browser = server_user_browser_dashboard
    clp_a, clp_a_lessons = curated_list_pages_with_lessons_and_placeholders[0]
    module_page = CuratedListPageFactory(parent=domestic_homepage, title='Test module page')
    lesson_page = DetailPageFactory(parent=module_page, title='test detail page 1')
    DetailPageFactory(parent=module_page, title='test detail page 2')

    visit_page(live_server, browser, None, 'Dashboard', endpoint=constants.DASHBOARD_URL)
    should_not_see_any_element(browser, DashboardReadingProgress)
    # Setting a lesson complete should show progress card with 1/1 complete
    mock_get_lesson_completed.return_value = {'result': 'ok', 'lesson_completed': [
        {'lesson': lesson_page.id}
    ]}

    visit_page(live_server, browser, None, 'Dashboard', endpoint=constants.DASHBOARD_URL)
    should_see_all_elements(browser, DashboardReadingProgress)

    check_topic_read_progress(browser, clp_a, clp_a_lessons)
