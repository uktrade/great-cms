from io import BytesIO
from urllib.parse import urljoin

import allure
import pytest
from PIL import Image
from pytest_bdd import scenarios, given, when, then, parsers
from selenium.common.exceptions import NoSuchElementException


scenarios('home_page.feature')


def convert_png_to_jpg(screenshot_png):
    raw_image = Image.open(BytesIO(screenshot_png))
    image = raw_image.convert('RGB')
    with BytesIO() as f:
        image.save(f, format='JPEG', quality=90)
        return f.getvalue()


def attach_jpg_screenshot(browser, page_name):
    screenshot_png = browser.get_screenshot_as_png()
    screenshot_jpg = convert_png_to_jpg(screenshot_png)
    allure.attach(
        screenshot_jpg,
        name=page_name,
        attachment_type=allure.attachment_type.JPG
    )


@given(parsers.cfparse('"{actor_alias}" decided to visit the home page'))
@given(parsers.cfparse('"{actor_alias}" is on the home page'))
def visit_landing_page(actor_alias, browser, visit_home_page):
    pass


@then(parsers.cfparse('"{actor_alias}" should be on the home page'))
def should_be_on_home_page(actor_alias, browser):
    attach_jpg_screenshot(browser, 'home page')
    logo = browser.find_element_by_css_selector('#great-mvp-header-logo')
    assert logo.is_displayed()


@then(parsers.cfparse('"{actor_alias}" should not see errors'))
def should_not_see_errors(actor_alias, browser):
    with pytest.raises(NoSuchElementException):
        browser.find_element_by_css_selector('.message.error')


@when(parsers.cfparse('"{actor_alias}" decided to go to "{slug}" page'))
def visit_page_by_slug(actor_alias, slug, browser):
    browser.get(urljoin(browser.current_url, slug))


@then(parsers.cfparse('"{actor_alias}" should be on the 404 page'))
def should_be_on_404_page(actor_alias, browser):
    attach_jpg_screenshot(browser, '404 page')
    assert 'This page cannot be found' in browser.page_source
