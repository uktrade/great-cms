# -*- coding: utf-8 -*-
import logging
import random
from typing import List

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver

from core import cms_slugs
from directory_constants import choices
from tests.browser.common_selectors import DashboardModalLetsGetToKnowYou
from tests.browser.steps import (
    should_not_see_any_element,
    should_not_see_errors,
    should_see_all_elements,
    visit_page,
)
from tests.browser.util import (
    attach_jpg_screenshot,
    find_element,
    selenium_action,
    try_alternative_click_on_exception,
)

pytestmark = [
    pytest.mark.browser,
    pytest.mark.dashboard,
]

logger = logging.getLogger(__name__)


def select_random_sample_sectors() -> List[str]:
    logger.info('Select random sample of sectors')
    sector_labels = [label for _, label in choices.SECTORS]
    sectors = random.sample(sector_labels, random.randint(1, 5))
    logger.info(f'Selected random sample of sectors: {sectors}')
    return sectors


def enter_and_submit_industries(browser, industries):
    logger.info('Enter sector names: %s', industries)
    industries_input = find_element(browser, DashboardModalLetsGetToKnowYou.INDUSTRIES_INPUT)
    for industry in industries:
        industries_input.send_keys(industry)
        industries_input.send_keys(Keys.ENTER)

    attach_jpg_screenshot(browser, 'After entering industries', selector=DashboardModalLetsGetToKnowYou.MODAL)

    with selenium_action(browser, 'Failed to submit industries'):
        continue_button = find_element(browser, DashboardModalLetsGetToKnowYou.SUBMIT)
        with try_alternative_click_on_exception(browser, continue_button):
            continue_button.click()

    should_not_see_errors(browser)
    attach_jpg_screenshot(browser, 'Dashboard with success query parameter')


def should_see_lets_get_to_know_you_modal(browser: WebDriver):
    logger.info('Should see "Lets get to know you modal"')
    should_see_all_elements(browser, DashboardModalLetsGetToKnowYou)


def should_not_see_lets_get_to_know_you_modal(browser: WebDriver):
    logger.info('Should NOT see "Lets get to know you modal"')
    should_not_see_any_element(browser, DashboardModalLetsGetToKnowYou)


def test_dashboard_welcome(
    mock_dashboard_profile_events_opportunities,
    mock_all_dashboard_and_export_plan_requests_and_responses,
    curated_list_pages_with_lessons,
    server_user_browser_dashboard,
    client,
):
    logger.info('Should see dashboard welcome')
    live_server, user, browser = server_user_browser_dashboard
    try:
        user.first_name = 'TEST USER'
        client.force_login(user)
        visit_page(live_server, browser, None, 'Dashboard', endpoint=cms_slugs.DASHBOARD_URL)
        welcome = browser.find_element(By.CSS_SELECTOR, 'h1#great-hero-welcome')
        assert welcome.text == 'Dashboard'
        user.first_name = None
        client.force_login(user)
        visit_page(live_server, browser, None, 'Dashboard', endpoint=cms_slugs.DASHBOARD_URL)
        welcome = browser.find_element(By.CSS_SELECTOR, 'h1#great-hero-welcome')
        assert welcome.text == 'Dashboard'

    except AssertionError:
        attach_jpg_screenshot(browser, 'Dashboard view')
        raise
