from selenium.webdriver.common.by import By

from utils.test_helpers import TestHelper


# this represents a webpage and should find elements and have methods to interact with the elements
class InternationalHomePage(TestHelper):
    # locator
    ENDPOINT = 'international'
    H1_TEXT = (By.TAG_NAME, 'h1')
    CONTACT_BUTTON = (By.LINK_TEXT, 'Contact')

    def navigate_to_international_home(self):
        self.navigate(f'{self.base_url}{self.ENDPOINT}')

    def get_h1_text(self):
        return self.get_element_text(self.H1_TEXT)

    def is_contact_button_visible(self):
        return self.is_visible(self.CONTACT_BUTTON)

    def click_contact_button(self):
        self.do_click(self.CONTACT_BUTTON)
