# -*- coding: utf-8 -*-
import logging
from enum import EnumMeta
from typing import List
from urllib.parse import urljoin

from django.urls import reverse
from pytest_django.live_server_helper import LiveServer
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.remote.webdriver import WebDriver

from tests.browser.util import attach_jpg_screenshot, is_element_visible

logger = logging.getLogger(__name__)


def visit_page(
    live_server: LiveServer,
    browser: WebDriver,
    view_name: str,
    page_name: str,
    check_for_errors: bool = True,
    *,
    endpoint: str = None,
):
    logger.info('Visit %s page', page_name)
    if view_name and not endpoint:
        url = urljoin(live_server.url, reverse(view_name))
    else:
        url = urljoin(live_server.url, endpoint)
    browser.get(url)
    attach_jpg_screenshot(browser, f'Visited {page_name}')
    if check_for_errors:
        should_not_see_errors(browser)


def should_see_all_expected_page_sections(browser: WebDriver, selector_enums: List[EnumMeta]):
    logger.info('Should see all expected page sections')
    attach_jpg_screenshot(browser, f'View of the whole page: {browser.current_url}')
    for selector_enum in selector_enums:
        should_see_all_elements(browser, selector_enum)


def should_see_all_elements(browser: WebDriver, selectors_enum: EnumMeta):
    logger.info('Should see all elements from: %s', selectors_enum)
    for selector in selectors_enum:
        if not selector.value:
            continue
        if not selector.is_visible:
            continue
        if selector.name in ['CONTAINER', 'MODAL']:
            attach_jpg_screenshot(browser, f'{selectors_enum.__name__} container', selector=selector)
        error = f'Expected element "{selector}" is not visible'
        if not is_element_visible(browser, selector):
            attach_jpg_screenshot(browser, error)
        assert is_element_visible(browser, selector), error
    logger.info(f'All elements from {selectors_enum} are visible on {browser.current_url}')


def should_not_see_element(browser, selector):
    logger.info('Should not see element: %s', selector)
    if not selector.is_visible:
        return
    assertion_error = f'Unexpected element is visible "{selector}"'
    try:
        assert not is_element_visible(browser, selector), assertion_error
    except AssertionError:
        attach_jpg_screenshot(browser, assertion_error)
        raise
    except StaleElementReferenceException:
        attach_jpg_screenshot(browser, 'StaleElementReferenceException')
        raise


def should_not_see_any_element(browser, selectors_enum):
    logger.info('Should not see elements from: %s', selectors_enum)
    for selector in selectors_enum:
        if not selector.is_visible:
            continue
        assertion_error = f'Unexpected element is visible "{selector}"'
        try:
            assert not is_element_visible(browser, selector), assertion_error
        except AssertionError:
            attach_jpg_screenshot(browser, assertion_error)
            raise
        except StaleElementReferenceException:
            attach_jpg_screenshot(browser, 'StaleElementReferenceException')
            raise


def should_not_see_errors(browser):
    logger.info('Should not see errors')
    assertion_error = ''
    page_source = browser.page_source
    try:
        assertion_error = f'500 ISE on {browser.current_url}'
        assert 'there is a problem with the service' not in page_source, assertion_error
        assert 'Internal Server Error' not in page_source, assertion_error
        assertion_error = f'404 Not Found on {browser.current_url}'
        assert 'This page cannot be found' not in page_source, assertion_error
        assertion_error = f'Unexpected Error on {browser.current_url}'
        assert 'Unexpected Error' not in page_source, assertion_error
        assertion_error = f'Error fetching data on {browser.current_url}'
        assert 'Error fetching data' not in page_source, assertion_error
        assertion_error = f'A server error occurred on {browser.current_url}'
        assert 'A server error occurred' not in page_source, assertion_error
    except AssertionError:
        attach_jpg_screenshot(browser, assertion_error)
        raise
