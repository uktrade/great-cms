import pytest
from tests.browser.common_selectors import Header, SignUpModal
from tests.browser.util import attach_jpg_screenshot, is_element_present

pytestmark = pytest.mark.browser


def test_anonymous_user_should_not_see_header_elements_for_authenticated_users(
        browser, visit_home_page
):
    attach_jpg_screenshot(browser, 'home page')
    for selector in Header:
        if not selector.is_authenticated:
            element = browser.find_element(selector.by, selector.selector)
            assert element.is_displayed()
        else:
            assert not is_element_present(browser, selector), (
                f'Element "{selector}" should not be present on the home page'
            )


def test_anonymous_user_should_see_sign_up_modal(browser, visit_home_page):
    attach_jpg_screenshot(browser, 'home page')
    for selector in SignUpModal:
        element = browser.find_element(selector.by, selector.selector)
        assert element.is_displayed(), f'Expected element "{selector}" is not visible'
