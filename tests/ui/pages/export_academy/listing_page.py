from selenium.webdriver.common.by import By

from pages.export_academy.base_ea_page import BaseEAPage
from utils.test_helpers import MOBILE_DEVICE


class ListingPage(BaseEAPage):
    def navigate_to_listing_page(self):
        self.navigate(f'{self.base_url}export-academy/events/')

    def get_full_text_of_first_event_list_card(self):
        card = self.get_first_event_card()
        return card.find_element(By.CLASS_NAME, 'details-text').text

    def get_text_overflow_visibility_of_first_event_list_card(self):
        card = self.get_first_event_card()
        return card.find_element(By.CLASS_NAME, 'details-text').value_of_css_property('overflow')

    def get_chevron_transform_of_first_event_list_card(self):
        card = self.get_first_event_card()
        element = card.find_element(By.CSS_SELECTOR, '.show-more details[open] summary')
        # approach to get css pseudo element see here - https://www.lambdatest.com/blog/handling-pseudo-elements-in-css-with-selenium/ # noqa
        transform_value = self.driver.execute_script(
            'return window.getComputedStyle(arguments[0], "::before").getPropertyValue("transform");', element
        )  # noqa
        return transform_value

    def click_show_more_first_event_list_card(self):
        card = self.get_first_event_card()
        card.find_element(By.TAG_NAME, 'summary').click()

    def get_summary_button_text_first_event_list_card(self):
        card = self.get_first_event_card()
        return card.find_element(By.TAG_NAME, 'summary').text

    def click_register_on_first_event_list_card(self):
        card = self.get_first_event_card()
        card.find_element(By.LINK_TEXT, 'Register').click()

    def get_first_event_card(self):
        event_cards = self.find_elements((By.CLASS_NAME, 'event-list-card'))
        if len(event_cards) > 0:
            return event_cards[0]

        raise 'no event cards'

    def get_filter_options_displayed(self, filter_category, js_enabled=True):
        if self.device_type is MOBILE_DEVICE:
            self.do_click((By.LINK_TEXT, 'Filters'))

        # ec.wait seems to timeout when waiting for an input element hence selenium's self.driver.find_element
        # as opposed to self.find_element (which uses ec.wait behind the scenes)
        category_dropdown = self.driver.find_element(
            By.XPATH,
            f"//li[@class='filter-section']/input[@id='{filter_category}']/following-sibling::div[contains(@class,'options')]",  # noqa
        )

        # storing result as opposed to returning so we can close on mobile.
        # closing first and then checking if displayed will throw a stale element error
        category_displayed = category_dropdown.is_displayed()

        if self.device_type is MOBILE_DEVICE and js_enabled:
            self.do_click((By.LINK_TEXT, 'Cancel'))

        return category_displayed

    def get_filter_option_checked(self, filter):
        option = self.driver.find_element(By.XPATH, f"//input[@value='{filter}']")
        return option.is_selected()

    def click_filters(self, filter_category, filter_values: list, js_enabled=True):
        if not self.get_filter_options_displayed(filter_category):
            if self.device_type is MOBILE_DEVICE:
                self.do_click((By.LINK_TEXT, 'Filters'))
            self.do_click(
                (
                    By.XPATH,
                    f"//li[@class='filter-section']/input[@id='{filter_category}']/following-sibling::label[contains(@for,'{filter_category}')]",  # noqa
                )
            )

        for value in filter_values:
            el = self.driver.find_element(By.XPATH, f"//input[@value='{value}']")
            el.click()

        if self.device_type is MOBILE_DEVICE and js_enabled:
            self.do_click((By.LINK_TEXT, 'Apply filters'))

    def click_update_results(self):
        self.do_click((By.XPATH, '//input[@value="Update results"]'))
