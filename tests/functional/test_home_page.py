from io import BytesIO

import allure
import pytest
from PIL import Image
from selenium.common.exceptions import NoSuchElementException


def convert_png_to_jpg(screenshot_png):
    raw_image = Image.open(BytesIO(screenshot_png))
    image = raw_image.convert("RGB")
    with BytesIO() as f:
        image.save(f, format="JPEG", quality=90)
        return f.getvalue()


def attach_jpg_screenshot(browser, page_name):
    screenshot_png = browser.get_screenshot_as_png()
    screenshot_jpg = convert_png_to_jpg(screenshot_png)
    allure.attach(
        screenshot_jpg,
        name=page_name,
        attachment_type=allure.attachment_type.JPG
    )


@allure.step("check if on home page")
def should_be_on_home_page(browser):
    attach_jpg_screenshot(browser, 'home page')
    logo = browser.find_element_by_css_selector("body > header > div > a > img")
    assert logo.is_displayed()


@allure.step("check if no errors are visible")
def should_not_see_errors(browser):
    with pytest.raises(NoSuchElementException):
        browser.find_element_by_css_selector(".message.error")


def test_should_not_see_errors_on_home_page(browser, visit_home_page):
    should_be_on_home_page(browser)
    should_not_see_errors(browser)
