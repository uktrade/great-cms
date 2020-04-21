# -*- coding: utf-8 -*-
from typing import List
from urllib.parse import urljoin

from django.urls import reverse
from selenium.webdriver.remote.webdriver import WebDriver

import allure
from pytest_django.live_server_helper import LiveServer
from tests.browser.common_selectors import SelectorsEnum
from tests.browser.util import (
    attach_jpg_screenshot,
    should_not_see_errors,
    should_see_all_elements,
)


@allure.step('Visit {page_name} page')
def visit_page(
    live_server: LiveServer,
    browser: WebDriver,
    view_name: str,
    page_name: str,
    check_for_errors: bool = True,
):
    target_markets_url = urljoin(live_server.url, reverse(view_name))
    browser.get(target_markets_url)
    attach_jpg_screenshot(browser, f'Visited {page_name}')
    if check_for_errors:
        should_not_see_errors(browser)


@allure.step('Should see all expected page sections')
def should_see_all_expected_page_sections(
    browser: WebDriver, selector_enums: List[SelectorsEnum]
):
    for selector_enum in selector_enums:
        should_see_all_elements(browser, selector_enum)
