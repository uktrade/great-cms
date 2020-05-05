# -*- coding: utf-8 -*-
from time import sleep

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver

import allure
import environ
from tests.browser.common_selectors import (
    Breadcrumbs,
    DashboardModalLetsGetToKnowYou,
    HeaderCommon,
    LearnHowToExportCategories,
    LearnHowToExportIntroduction,
    LearnHowToExportLanding,
)
from tests.browser.steps import (
    should_not_see_errors,
    should_see_all_elements,
    should_see_all_expected_page_sections,
)
from tests.browser.test_dashboard import should_not_see_lets_get_to_know_you_modal
from tests.browser.util import attach_jpg_screenshot, find_element, selenium_action

pytestmark = [
    pytest.mark.browser,
    pytest.mark.learn,
]


@pytest.fixture(scope='function')
def single_browser_session():
    options = Options()
    env = environ.Env()
    headless = env.bool('HEADLESS', True)
    if headless:
        options.add_argument('--headless')
        options.add_argument('--window-size=1600x2200')
        options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(options=options)
    yield browser
    browser.quit()


@pytest.fixture(scope='function')
def server_logged_in_user_single_browser_session(
    settings,
    live_server,
    single_browser_session,
    user,
    client,
    mock_get_company_profile,
    domestic_site_browser_tests,
    how_to_export_introduction_pages,
):
    client.force_login(user)
    browser = single_browser_session

    browser.get(f'{live_server.url}/dashboard/')

    browser.add_cookie({'name': settings.SSO_SESSION_COOKIE, 'value': user.session_id, 'path': '/'})
    browser.refresh()
    should_not_see_errors(browser)

    return live_server, user, browser


@allure.step('Dismiss the "Lets Get To Know You" modal')
def dismiss_modal(browser: WebDriver):
    generic_content = find_element(browser, DashboardModalLetsGetToKnowYou.GENERIC_CONTENT)
    with selenium_action(browser, 'Failed to dismiss the modal'):
        generic_content.click()
    should_not_see_lets_get_to_know_you_modal(browser)


@allure.step('Click on the Leaning link')
def click_on_learning_link(browser: WebDriver):
    leaning_link = find_element(browser, HeaderCommon.LEARNING)
    with selenium_action(browser, 'Failed to click on header "Learning" link'):
        leaning_link.click()
    should_not_see_errors(browser)
    attach_jpg_screenshot(browser, 'How to export landing page')


@allure.step('Decide to learn how to export')
def decide_to_learn_how_to_export(browser: WebDriver):
    learn_how_to_export_button = find_element(browser, LearnHowToExportLanding.LEARN_HOW_TO_EXPORT)
    with selenium_action(browser, 'Failed to click on "Learn how to export" button'):
        learn_how_to_export_button.click()
    should_not_see_errors(browser)
    attach_jpg_screenshot(browser, 'How to export introduction')


@allure.step('Click through carousel')
def click_through_carousel(browser: WebDriver):
    carousel = find_element(browser, LearnHowToExportIntroduction.CONTAINER)
    continue_button = find_element(browser, LearnHowToExportIntroduction.CONTINUE)
    attach_jpg_screenshot(browser, f'Carousel step - 1', element=carousel)
    for step in range(2, 4):
        with selenium_action(browser, 'Failed to click on "Continue" button'):
            continue_button.click()
        attach_jpg_screenshot(browser, f'Carousel step - {step}', element=carousel)
        sleep(1)

    with selenium_action(browser, 'Failed to click on "Continue" button'):
        continue_button.click()


@allure.step('Should be on the "Learn how to export categories" page')
def should_be_on_learn_how_to_export_categories_page(browser: WebDriver):
    should_see_all_expected_page_sections(browser, [Breadcrumbs, LearnHowToExportCategories])


def test_first_time_visitor_should_be_able_to_get_to_learn_how_to_export_landing_page(
    server_user_browser_dashboard, mock_dashboard_profile_events_opportunities,
):
    live_server, user, browser = server_user_browser_dashboard
    dismiss_modal(browser)

    click_on_learning_link(browser)
    should_see_all_elements(browser, LearnHowToExportLanding)


def test_first_time_visitor_should_get_to_learn_how_to_export_page_via_introduction_carousel(
    server_user_browser_dashboard, mock_dashboard_profile_events_opportunities,
):
    live_server, user, browser = server_user_browser_dashboard
    dismiss_modal(browser)

    click_on_learning_link(browser)
    should_see_all_elements(browser, LearnHowToExportLanding)

    decide_to_learn_how_to_export(browser)
    should_see_all_elements(browser, LearnHowToExportIntroduction)

    click_through_carousel(browser)
    should_be_on_learn_how_to_export_categories_page(browser)


def test_second_time_visitor_should_be_redirected_to_learn_how_to_export_categories_page(
    server_user_browser_dashboard, mock_dashboard_profile_events_opportunities,
):
    live_server, user, browser = server_user_browser_dashboard
    dismiss_modal(browser)

    click_on_learning_link(browser)
    should_see_all_elements(browser, LearnHowToExportLanding)

    decide_to_learn_how_to_export(browser)
    should_see_all_elements(browser, LearnHowToExportIntroduction)

    click_through_carousel(browser)
    should_be_on_learn_how_to_export_categories_page(browser)

    click_on_learning_link(browser)
    should_be_on_learn_how_to_export_categories_page(browser)
