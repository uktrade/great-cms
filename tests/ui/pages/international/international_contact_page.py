from selenium.webdriver.common.by import By

from utils.test_helpers import TestHelper


# this represents a webpage and should find elements and have methods to interact with the elements
class InternationalContactPage(TestHelper):
    # locator
    ENDPOINT = 'international/contact'
    EXPANDING_RADIO = (By.ID, 'id_choice_0-label')
    CONTINUE_BUTTON = (By.XPATH, '//button[text()="Continue"]')

    def navigate_to_international_contact(self):
        self.navigate(f'{self.base_url}{self.ENDPOINT}')

    def select_expanding_option(self):
        self.do_click(self.EXPANDING_RADIO)

    def click_continue(self):
        self.do_click(self.CONTINUE_BUTTON)
