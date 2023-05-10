from selenium.webdriver.common.by import By

from utils.test_helpers import TestHelper


class BaseEAPage(TestHelper):
    def click_accept_cookies(self):
        accept_cookies_button = (By.LINK_TEXT, 'Accept all cookies')
        self.do_click(accept_cookies_button)

    def click_breadcrumb(self, link_text):
        breadcrumbs = self.find_element((By.CLASS_NAME, 'breadcrumbs'))
        breadcrumb = breadcrumbs.find_element(By.LINK_TEXT, link_text)
        breadcrumb.click()

    def click_card_link(self, id):
        card = (By.ID, id)
        self.do_click(card)
