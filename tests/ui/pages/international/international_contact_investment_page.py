from selenium.webdriver.common.by import By

from utils.test_helpers import TestHelper


class InternationalContactInvestmentPage(TestHelper):
    # locator
    ENDPOINT = 'international/invest/contact/'
    GIVEN_NAME_FIELD = (By.ID, 'id_given_name')
    INDUSTRY_SELECT = (By.ID, 'id_industry')
    SUBMIT_BUTTON = (By.XPATH, '//*[@id="content"]/div/div/form/button')

    def navigate_to_international_contact_invest(self):
        self.navigate(f'{self.base_url}{self.ENDPOINT}')

    def enter_given_name(self, input_text):
        self.do_send_keys(self.GIVEN_NAME_FIELD, input_text)

    def select_your_industry(self, option):
        self.do_select(self.INDUSTRY_SELECT, option)

    def get_selected_industry(self):
        return self.get_selected_option(self.INDUSTRY_SELECT)

    def click_submit(self):
        self.do_click(self.SUBMIT_BUTTON)
