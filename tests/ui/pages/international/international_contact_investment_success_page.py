from utils.test_helpers import TestHelper


class InternationalContactInvestmentSuccessPage(TestHelper):
    # locator
    ENDPOINT = 'international/invest/contact/success/'

    def navigate_to_international_contact_invest_success(self):
        self.navigate(f'{self.base_url}{self.ENDPOINT}')

    def get_page(self):
        return self.driver.page_source
