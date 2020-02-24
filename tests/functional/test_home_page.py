from io import BytesIO

import allure
import pytest
from PIL import Image
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist


def convert_png_to_jpg(screenshot_png: bytes):
    raw_image = Image.open(BytesIO(screenshot_png))
    image = raw_image.convert("RGB")
    with BytesIO() as f:
        image.save(f, format="JPEG", quality=90)
        return f.getvalue()


def attach_jpg_screenshot(browser: Browser, page_name: str):
    screenshot_png = browser.driver.get_screenshot_as_png()
    screenshot_jpg = convert_png_to_jpg(screenshot_png)
    allure.attach(
        screenshot_jpg,
        name=page_name,
        attachment_type=allure.attachment_type.JPG
    )


@allure.step("check if on home page")
def should_be_on_home_page(browser):
    attach_jpg_screenshot(browser, 'home page')
    browser.find_by_css("body > header > div > a > img")
    browser.is_element_visible_by_css("body > header > div > a > img")


@allure.step("check if no errors are visible")
def should_not_see_errors(browser):
    with pytest.raises(ElementDoesNotExist):
        browser.find_by_css(".message.error").first


def test_should_not_see_errors_on_home_page(browser, visit_home_page):
    should_be_on_home_page(browser)
    should_not_see_errors(browser)
