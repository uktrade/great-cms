import pytest
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from pages.export_academy.listing_page import ListingPage


class TestListingPageLoggedOutNoJS:
    @pytest.mark.parametrize('driver', [True], indirect=True)
    def test_filters_expanded_on_page_load(self, driver):
        test_name = 'EA:listing:logged_out:no_js:test_filters_expanded_on_page_load'

        if self.should_skip_test(driver):
            pytest.skip('Non-js only implemented for Chrome')

        try:
            listing_page = ListingPage(driver)
            listing_page.navigate_to_listing_page()

            filter_categories = ['Content', 'Format', 'Date']
            for category in filter_categories:
                assert listing_page.get_filter_options_displayed(category, js_enabled=False)

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    @pytest.mark.parametrize('driver', [True], indirect=True)
    def test_page_updates_when_update_results_clicked(self, driver):
        test_name = 'EA:listing:logged_out:no_js:test_page_updates_when_update_results_clicked'

        if self.should_skip_test(driver):
            pytest.skip('Non-js only implemented for Chrome')

        try:
            listing_page = ListingPage(driver)
            listing_page.navigate_to_listing_page()

            events_form = listing_page.find_element((By.ID, 'events-form'))

            listing_page.click_filters('Content', ['masterclass'], js_enabled=False)
            listing_page.click_update_results()

            # use stale element error as a proxy for checking if the page has been refreshed
            # i.e. if the page has been refreshed the reference to events_form will be stale
            try:
                events_form.is_displayed()
                assert False
            except StaleElementReferenceException:
                assert True

            assert listing_page.get_filter_options_displayed('Content', js_enabled=False)
            assert listing_page.get_filter_option_checked('masterclass')

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def should_skip_test(self, driver):
        # desktops have browserName, mobiles have javascriptEnabled keys

        if 'browserName' in driver.capabilities:
            return driver.capabilities['browserName'] != 'chrome'
        elif 'javascriptEnabled' in driver.capabilities:
            return driver.capabilities['javascriptEnabled']

        return False
