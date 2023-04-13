from time import sleep

import pytest

from pages.export_academy.listing_page import ListingPage
from utils.test_helpers import MOBILE_DEVICE, SLEEP_TIME_BEFORE_CHECKING_URL_SECS


@pytest.fixture()
def listing_page(driver):
    listing_page = ListingPage(driver)
    listing_page.navigate_to_listing_page()
    listing_page.click_accept_cookies()
    return listing_page


class TestListingPageLoggedOut:
    def test_breadcrumb_great(self, listing_page):
        test_name = 'EA:listing:logged_out:test_breadcrumb_great'

        if listing_page.device_type is MOBILE_DEVICE:
            pytest.skip('No breadcrumbs on mobile')

        try:
            listing_page.click_breadcrumb('great.gov.uk')
            # give the browser some time to respond to the click before checking the url
            # see here https://www.browserstack.com/guide/thread-sleep-in-selenium
            sleep(SLEEP_TIME_BEFORE_CHECKING_URL_SECS)
            assert listing_page.driver.current_url == f'{listing_page.base_url}'

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_breadcrumb_ukea(self, listing_page):
        test_name = 'EA:listing:logged_out:test_breadcrumb_ukea'

        if listing_page.device_type is MOBILE_DEVICE:
            pytest.skip('No breadcrumbs on mobile')

        try:
            listing_page.click_breadcrumb('UK Export Academy')
            sleep(SLEEP_TIME_BEFORE_CHECKING_URL_SECS)
            assert listing_page.driver.current_url == f'{listing_page.base_url}export-academy/'

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_register_button(self, listing_page):
        test_name = 'EA:listing:logged_out:test_register_button'
        try:
            listing_page.click_register_on_first_event_list_card()
            sleep(SLEEP_TIME_BEFORE_CHECKING_URL_SECS)
            assert (
                listing_page.driver.current_url
                == 'https://www.events.great.gov.uk/ereg/newreg.php?eventid=200236512&language=eng'  # noqa: W503
            )

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_details_text_visibility(self, listing_page):
        test_name = 'EA:listing:logged_out:test_details_text_visibility'
        try:
            assert listing_page.get_text_overflow_visibility_of_first_event_list_card() == 'hidden'
            listing_page.click_show_more_first_event_list_card()
            assert listing_page.get_text_overflow_visibility_of_first_event_list_card() == 'visible'

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_show_more_button_text(self, listing_page):
        test_name = 'EA:listing:logged_out:test_show_more_button_text'
        try:
            assert listing_page.get_summary_button_text_first_event_list_card() == 'Show more'

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_show_less_button_text(self, listing_page):
        test_name = 'EA:listing:logged_out:test_show_less_button_text'
        try:
            listing_page.click_show_more_first_event_list_card()
            assert listing_page.get_summary_button_text_first_event_list_card() == 'Show less'

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_show_more_chevron_orientation(self, listing_page):
        test_name = 'EA:listing:logged_out:test_show_more_chevron_orientation'

        # if listing_page.driver.capabilities['browserName'] == 'firefox':
        #     pytest.skip("Matrix value of 0")

        try:
            listing_page.click_show_more_first_event_list_card()
            # we get a matrix back from selenium's computed css property. below assertion corresponds to rotate270deg
            # see https://angrytools.com/css-generator/transform/ for a tool to compute alternative rotations
            assert listing_page.get_chevron_transform_of_first_event_list_card() == 'matrix(0, -1, 1, 0, 0, 0)'

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_filter_categories_expanded(self, listing_page):
        test_name = 'EA:listing:logged_out:test_filter_categories_expanded'
        try:
            filter_categories = ['Content', 'Format']
            filter_options = ['masterclass', 'essentials', 'sector', 'market', 'online', 'in_person']
            listing_page.click_filters(filter_categories[0], filter_options[0:4])
            listing_page.click_filters(filter_categories[1], filter_options[4:])

            for category in filter_categories:
                assert listing_page.get_filter_options_displayed(category)

            assert listing_page.get_filter_options_displayed('Date') is False

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e

    def test_correct_filters_selected(self, listing_page):
        test_name = 'EA:listing:logged_out:test_correct_filters_selected'
        try:
            filter_categories = ['Content', 'Format', 'Date']
            active_filters = ['masterclass', 'market', 'online', 'all']
            inactive_filters = [
                'essentials',
                'sector',
                'in_person',
                'today',
                'tomorrow',
                'this_week',
                'next_week',
                'this_month',
                'next_month',
            ]

            listing_page.click_filters(filter_categories[0], active_filters[:2])
            listing_page.click_filters(filter_categories[1], active_filters[2:3])
            listing_page.click_filters(filter_categories[2], active_filters[3:])

            for filter in active_filters:
                assert listing_page.get_filter_option_checked(filter) is True

            for filter in inactive_filters:
                assert listing_page.get_filter_option_checked(filter) is False

            listing_page.label_test_in_browserstack_console('passed', test_name)
        except AssertionError as e:
            listing_page.label_test_in_browserstack_console('failed', f'{test_name} {repr(e)}')
            raise e


#     # below test is redundant because in this case the page_source always contains full_text
#     # with the visibility controlled via css overflow. Included as an examplar.

#     # def test_full_text_displayed(self, listing_page):
#     #     listing_page.click_show_more_first_event_list_card()

#     #     # there is a difference in special character representation between page_source and .text
#     #     # e.g. You'll is You'll in full_text but You&#x27;ll in page_source() below regex / re.sub
#     #     # substitutes any non-Word or digit with a blank space.
#     #     pattern = r"\W|\d"

#     #     first_event_text = listing_page.get_full_text_of_first_event_list_card()
#     #     first_event_text = re.sub(pattern,'',first_event_text)

#     #     page_source = listing_page.driver.page_source
#     #     page_source = re.sub(pattern,'',page_source)

#     #     assert first_event_text in page_source
