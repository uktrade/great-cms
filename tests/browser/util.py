# -*- coding: utf-8 -*-
import logging
import sys
import traceback
from contextlib import contextmanager
from io import BytesIO
from typing import List, Union

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

import allure
from PIL import Image
from tests.browser.common_selectors import Selector, SelectorsEnum

logger = logging.getLogger(__name__)


def convert_png_to_jpg(screenshot_png: bytes) -> bytes:
    raw_image = Image.open(BytesIO(screenshot_png))
    image = raw_image.convert('RGB')
    with BytesIO() as f:
        image.save(f, format='JPEG', quality=90)
        return f.getvalue()


def attach_jpg_screenshot(
    browser: WebDriver,
    page_name: str,
    *,
    selector: Union[Selector, SelectorsEnum] = None,
    element: WebElement = None,
):
    if selector:
        element = find_element(browser, selector)
        screenshot_png = element.screenshot_as_png
    elif element:
        screenshot_png = element.screenshot_as_png
    else:
        screenshot_png = browser.get_screenshot_as_png()
    screenshot_jpg = convert_png_to_jpg(screenshot_png)
    allure.attach(
        screenshot_jpg,
        name=page_name,
        attachment_type=allure.attachment_type.JPG,
        extension='jpg',
    )


def is_element_present(browser: WebDriver, selector: Selector) -> bool:
    """Check if sought element is present (doesn't have to be visible).

    If selector returns more than 1 element then find_element() will return the first
    element from the list.
    """
    is_present = True
    try:
        browser.find_element(by=selector.by, value=selector.selector)
    except NoSuchElementException:
        is_present = False
    return is_present


def is_element_visible(browser: WebDriver, selector: Selector) -> bool:
    """Check if sought element is visible.

    If element is not present it will also return False.
    """
    try:
        is_visible = browser.find_element(
            by=selector.by, value=selector.selector
        ).is_displayed()
    except NoSuchElementException:
        is_visible = False
    return is_visible


def find_element(browser: WebDriver, selector: Selector) -> WebElement:
    return browser.find_element(selector.by, selector.selector)


def find_elements(browser: WebDriver, selector: Selector) -> List[WebElement]:
    return browser.find_elements(selector.by, selector.selector)


def wait_for_element_visibility(
    driver: WebDriver, selector: Selector, *, time_to_wait: int = 3
):
    """Wait until element is visible."""
    locator = (selector.by, selector.selector)
    WebDriverWait(driver, time_to_wait).until(
        expected_conditions.visibility_of_element_located(locator)
    )


@contextmanager
def wait_for_text_in_element(
    driver: WebDriver, selector: Selector, text: str, *, time_to_wait: int = 3
):
    """Perform an action and wait until text is visible in specific element.

    Example:
        - click on a button and wait for its label's text to contain word 'Selected'

        label = Selector(By.ID, 'button_label')
        with wait_for_text_in_element(browser, label, 'Selected'):
            button.click()
    """
    yield
    locator = (selector.by, selector.selector)
    WebDriverWait(driver, time_to_wait).until(
        expected_conditions.text_to_be_present_in_element(locator, text)
    )


@allure.step('Should see all elements from: {selectors_enum}')
def should_see_all_elements(browser: WebDriver, selectors_enum: SelectorsEnum):
    for selector in selectors_enum:
        if not selector.value:
            continue
        if not selector.is_visible:
            continue
        if selector.name == 'CONTAINER':
            attach_jpg_screenshot(
                browser, f'{selectors_enum.__name__} container', selector=selector
            )
        error = f'Expected element "{selector}" is not visible'
        if not is_element_visible(browser, selector):
            attach_jpg_screenshot(browser, error)
        assert is_element_visible(browser, selector), error
    logger.info(
        f'All elements from {selectors_enum} are visible on {browser.current_url}'
    )


@allure.step('Should not see element: {selector}')
def should_not_see_element(browser, selector):
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


@allure.step('Should not see elements from: {selectors_enum}')
def should_not_see_any_element(browser, selectors_enum):
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


@allure.step('Should not see errors')
def should_not_see_errors(browser):
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
    except AssertionError:
        attach_jpg_screenshot(browser, assertion_error)
        raise


@contextmanager
def selenium_action(driver, message, *args):
    """This will:
        * print the custom assertion message
        * print the traceback (stack trace)
        * raise the original AssertionError exception

    :raises WebDriverException or NoSuchElementException
    """
    try:
        yield
    except (WebDriverException, NoSuchElementException, TimeoutException) as e:
        attach_jpg_screenshot(driver, message)
        browser = driver.capabilities.get('browserName', 'unknown browser')
        version = driver.capabilities.get('browserVersion', 'unknown version')
        platform = driver.capabilities.get('platformName', 'unknown platform')
        driver_version = 'unknown driver version'
        if browser == 'chrome':
            driver_version = driver.capabilities['chrome']['chromedriverVersion']
        if browser == 'firefox':
            driver_version = driver.capabilities['moz:geckodriverVersion']
        session_id = driver.session_id
        info = f'[{browser} v:{version} driver:{driver_version} os:{platform} session_id:{session_id}]'
        if args:
            message = message % args
        print(f'{info} - {message}')  # noqa T001
        e.args += (message,)
        _, _, tb = sys.exc_info()
        traceback.print_tb(tb)
        raise


@contextmanager
def try_alternative_click_on_exception(driver, element):
    """Try alternative click methods (JS or ActionChains) if regular way didn't work.

    JS workaround:
        Handle situations when clicking on element triggers:
        selenium.common.exceptions.ElementClickInterceptedException:
            Message: element click intercepted:
            Element <input id="id_terms"> is not clickable at point (714, 1235).
            Other element would receive the click: <label for="id_terms">...</label>
        See: https://stackoverflow.com/a/44916498

    ActionChains workaround:
        Handles situations when clicking on element triggers:
        selenium.common.exceptions.ElementNotInteractableException:
        Message: Element <a href="..."> could not be scrolled into view
        See: https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.common.action_chains
    """
    try:
        yield
    except ElementClickInterceptedException as e:
        logging.warning(
            f'Failed click intercepted. Will try JS workaround for: {e.msg}'
        )
        driver.execute_script('arguments[0].click();', element)
    except ElementNotInteractableException as e:
        logging.warning(
            f'Failed click intercepted. Will try ActionChains workaround for: {e.msg}'
        )
        action_chains = ActionChains(driver)
        action_chains.move_to_element(element)
        action_chains.click()
        action_chains.perform()
        logging.warning(f'ActionChains click workaround is done')
