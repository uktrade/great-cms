from io import BytesIO
from typing import List

import allure
from PIL import Image
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from tests.browser.common_selectors import Selector


def convert_png_to_jpg(screenshot_png: bytes) -> bytes:
    raw_image = Image.open(BytesIO(screenshot_png))
    image = raw_image.convert('RGB')
    with BytesIO() as f:
        image.save(f, format='JPEG', quality=90)
        return f.getvalue()


def attach_jpg_screenshot(
        browser: WebDriver, page_name: str, *, selector: Selector = None
):
    if selector:
        element = find_element(browser, selector)
        screenshot_png = element.screenshot_as_png
    else:
        screenshot_png = browser.get_screenshot_as_png()
    screenshot_jpg = convert_png_to_jpg(screenshot_png)
    allure.attach(
        screenshot_jpg,
        name=page_name,
        attachment_type=allure.attachment_type.JPG,
        extension='jpg'
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


def find_elements(browser: WebElement, selector: Selector) -> List[WebElement]:
    return browser.find_elements(selector.by, selector.selector)


def wait_for_element_visibility(
        driver: WebDriver, selector: Selector, *, time_to_wait: int = 3
):
    """Wait until element is visible."""
    locator = (selector.by, selector.selector)
    WebDriverWait(driver, time_to_wait).until(
        expected_conditions.visibility_of_element_located(locator)
    )
