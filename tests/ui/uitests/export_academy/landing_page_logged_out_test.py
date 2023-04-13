import time

import pytest
from selenium.common.exceptions import TimeoutException

from pages.export_academy.landing_page import LandingPage
from utils.test_helpers import SLEEP_TIME_BEFORE_CHECKING_URL_SECS


@pytest.fixture()
def landing_page(driver):
    landing_page = LandingPage(driver)
    landing_page.navigate_to_landing_page()
    try:
        landing_page.click_accept_cookies()
    except TimeoutException:
        # cookie modal only shown once in browserstack tests
        pass

    return landing_page


class TestLandingPageLoggedOut:
    def test_hero_cta_register_for_account(self, landing_page):
        test_name = 'EA:landing:logged_out:test_hero_cta_register_for_account'
        try:
            landing_page.click_hero_register_button()
            # give the browser some time to respond to the click before checking the url
            # see here https://www.browserstack.com/guide/thread-sleep-in-selenium
            time.sleep(SLEEP_TIME_BEFORE_CHECKING_URL_SECS)

            assert (
                landing_page.driver.current_url
                == 'https://www.events.great.gov.uk/ereg/newreg.php?eventid=200236512&language=eng'  # noqa: W503
            )
            landing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            landing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_breadcrumb_great(self, landing_page):
        test_name = 'EA:landing:logged_out:test_breadcrumb_great'
        try:
            landing_page.click_breadcrumb('great.gov.uk')
            time.sleep(SLEEP_TIME_BEFORE_CHECKING_URL_SECS)
            assert landing_page.driver.current_url == f'{landing_page.base_url}'
            landing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            landing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_essentials_card(self, landing_page):
        test_name = 'EA:landing:logged_out:test_essentials_card'
        try:
            landing_page.click_card_link('card-essentials-link')
            time.sleep(SLEEP_TIME_BEFORE_CHECKING_URL_SECS)
            assert landing_page.driver.current_url == f'{landing_page.base_url}export-academy/events/?type=essentials'
            landing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            landing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_masterclasses_card(self, landing_page):
        test_name = 'EA:landing:logged_out:test_masterclasses_card'
        try:
            landing_page.click_card_link('card-masterclasses-link')
            time.sleep(SLEEP_TIME_BEFORE_CHECKING_URL_SECS)
            assert landing_page.driver.current_url == f'{landing_page.base_url}export-academy/events/?type=masterclass'
            landing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            landing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_sector_markets_card(self, landing_page):
        test_name = 'EA:landing:logged_out:test_sector_markets_card'
        try:
            landing_page.click_card_link('card-sector & market-link')
            time.sleep(SLEEP_TIME_BEFORE_CHECKING_URL_SECS)
            assert (
                landing_page.driver.current_url
                == f'{landing_page.base_url}export-academy/events/?type=sector&type=market'  # noqa:W503
            )
            landing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            landing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_view_events_button(self, landing_page):
        test_name = 'EA:landing:logged_out:test_view_events_button'
        try:
            landing_page.click_view_all_events_button()
            time.sleep(SLEEP_TIME_BEFORE_CHECKING_URL_SECS)
            assert landing_page.driver.current_url == f'{landing_page.base_url}export-academy/events/?'
            landing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            landing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e
