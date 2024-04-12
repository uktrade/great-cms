from selenium.webdriver.common.by import By

from utils.test_helpers import TestHelper


class HomePage(TestHelper):
    # locator
    H1_TEXT = (By.TAG_NAME, 'h1')
    ACCEPT_COOKIES_BUTTON = (By.LINK_TEXT, 'Accept additional cookies')

    def navigate_to_home(self):
        self.navigate(f'{self.base_url}')

    def click_accept_cookies(self):
        self.do_click(self.ACCEPT_COOKIES_BUTTON)

    def get_h1_text(self):
        return self.get_element_text(self.H1_TEXT)
