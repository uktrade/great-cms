# -*- coding: utf-8 -*-
import logging
from random import choice
from typing import List
from unittest import mock

import pytest
from pytest_django.live_server_helper import LiveServer
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from core import cms_slugs
from sso import helpers as sso_helpers
from tests.browser.common_selectors import (
    DashboardReadingProgress,
    LessonPage,
    TopicLessonListing,
)
from tests.browser.steps import (
    should_not_see_element,
    should_see_all_elements,
    visit_page,
)
from tests.browser.util import attach_jpg_screenshot, selenium_action
from tests.unit.core.factories import (
    CuratedListPageFactory,
    DetailPageFactory,
    LessonPlaceholderPageFactory,
    ListPageFactory,
    TopicPageFactory,
)

pytestmark = [
    pytest.mark.browser,
    pytest.mark.lesson,
]

logger = logging.getLogger(__name__)


def visit_lesson_listing_page(live_server: LiveServer, browser: WebDriver, page_name: str, endpoint: str):
    logger.info('Visit lesson listing page: %s', page_name)
    visit_page(live_server, browser, '', page_name, endpoint=endpoint)
    should_see_all_elements(browser, TopicLessonListing)


def visit_lesson_page(live_server: LiveServer, browser: WebDriver, page_name: str, endpoint: str):
    logger.info('Visit %s page', page_name)
    visit_page(live_server, browser, '', page_name, endpoint=endpoint)
    should_see_all_elements(browser, LessonPage)


def open_random_lesson(browser: WebDriver):
    logger.info('Open random lesson on lesson listing page')
    lesson_links = browser.find_elements(
        by=TopicLessonListing.LESSON_LINKS.by,
        value=TopicLessonListing.LESSON_LINKS.selector,
    )
    lesson_link = choice(lesson_links)

    with selenium_action(browser, f'Failed to view lesson: {lesson_link.text}'):
        lesson_link.click()

    attach_jpg_screenshot(browser, 'Lesson page')


def check_topic_read_progress(browser: WebDriver, topic: ListPageFactory, lessons: List[DetailPageFactory]):
    logger.info('Check topics reading progress')
    attach_jpg_screenshot(browser, 'Topics reading progress', selector=DashboardReadingProgress.YOUR_PROGRESS_CARD)
    count_element = browser.find_element(By.CSS_SELECTOR, '#your-progress-card .progress-bar-text')
    count_text = count_element.text
    assert count_text == '1 / 2 lessons completed'


def test_can_view_lessons_from_different_topics(
    mock_get_lessons_completed,
    mock_dashboard_profile_events_opportunities,
    mock_all_dashboard_and_export_plan_requests_and_responses,
    curated_list_pages_with_lessons,
    server_user_browser_dashboard,
):
    live_server, user, browser = server_user_browser_dashboard
    clp_a, clp_a_lessons = curated_list_pages_with_lessons[0]
    clp_b, clp_b_lessons = curated_list_pages_with_lessons[1]

    visit_page(live_server, browser, None, 'Dashboard', endpoint=cms_slugs.DASHBOARD_URL)

    visit_lesson_listing_page(live_server, browser, 'Topic A', clp_a.url)
    visit_lesson_page(live_server, browser, 'Module A - Topic A - Lesson A1', clp_a_lessons[0].url)
    visit_lesson_page(live_server, browser, 'Module A - Topic A - Lesson A2', clp_a_lessons[1].url)

    visit_lesson_listing_page(live_server, browser, 'Topic B', clp_b.url)
    visit_lesson_page(live_server, browser, 'Topic B - Lesson B1', clp_b_lessons[0].url)
    visit_lesson_page(live_server, browser, 'Topic B - Lesson B2', clp_b_lessons[1].url)


@mock.patch.object(sso_helpers, 'get_lesson_completed')
def test_can_mark_lesson_as_read_and_check_read_progress_on_dashboard_page(
    mock_get_lesson_completed,
    mock_dashboard_profile_events_opportunities,
    mock_all_dashboard_and_export_plan_requests_and_responses,
    curated_list_pages_with_lessons,
    server_user_browser_dashboard,
    domestic_homepage,
):
    live_server, user, browser = server_user_browser_dashboard
    clp_a, clp_a_lessons = curated_list_pages_with_lessons[0]
    module_page = CuratedListPageFactory(parent=domestic_homepage, title='Test module page')
    topic_page = TopicPageFactory(parent=module_page, title='Module one, first topic')
    LessonPlaceholderPageFactory(
        title='Placeholder To Show They Do Not Interfere With Counts',
        parent=topic_page,
    )
    lesson_one = DetailPageFactory(
        parent=topic_page,
        title='test detail page 1',
        slug='test-detail-page-1',
    )
    DetailPageFactory(
        parent=topic_page,
        title='test detail page 2',
        slug='test-detail-page-2',
    )
    visit_page(live_server, browser, None, 'Dashboard', endpoint=cms_slugs.DASHBOARD_URL)
    should_not_see_element(browser, DashboardReadingProgress.LESSONS_COMPLETED_TEXT)
    # Setting a lesson complete should show progress card with 1/1 complete
    mock_get_lesson_completed.return_value = {'result': 'ok', 'lesson_completed': [{'lesson': lesson_one.id}]}

    visit_page(live_server, browser, None, 'Dashboard', endpoint=cms_slugs.DASHBOARD_URL)
    should_see_all_elements(browser, DashboardReadingProgress)
    check_topic_read_progress(browser, clp_a, clp_a_lessons)
