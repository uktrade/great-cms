import pytest



@allure.step('check if on home page')
def should_be_on_home_page(browser):
    attach_jpg_screenshot(browser, 'home page')
    logo = browser.find_element_by_css_selector('body > header > div > a > img')
    assert logo.is_displayed()


@allure.step('check if no errors are visible')
def should_not_see_errors(browser):
    with pytest.raises(NoSuchElementException):
        browser.find_element_by_css_selector('.message.error')


def test_should_not_see_errors_on_home_page(browser, visit_home_page):
    should_be_on_home_page(browser)
    should_not_see_errors(browser)
