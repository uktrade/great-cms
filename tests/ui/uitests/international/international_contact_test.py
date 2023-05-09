from pages.international.international_contact_investment_page import (
    InternationalContactInvestmentPage,
)
from pages.international.international_contact_investment_success_page import (
    InternationalContactInvestmentSuccessPage,
)
from pages.international.international_contact_page import InternationalContactPage
from pages.international.international_home_page import InternationalHomePage


# no raw selenium or direct interaction with selenium api should be in a test -
# - see https://seleniumjava.com/2016/05/08/do-not-use-webdriver-apis-in-the-test-script/
# apart from a page initialisation it should actually be pretty readable to a non-dev
def test_contact_expanding_unhappy(driver):
    home_page = InternationalHomePage(driver)
    home_page.navigate_to_international_home()
    home_page.click_contact_button()
    contact_page = InternationalContactPage(driver)
    contact_page.select_expanding_option()
    contact_page.click_continue()
    contact_investment_page = InternationalContactInvestmentPage(driver)
    contact_investment_page.enter_given_name(contact_investment_page.fake.name())
    contact_investment_page.select_your_industry('Aerospace')
    assert contact_investment_page.get_selected_industry() == 'Aerospace'
    contact_investment_page.click_submit()
    assert contact_investment_page.ENDPOINT == 'international/invest/contact/'


def test_contact_invest_success(driver):
    success_page = InternationalContactInvestmentSuccessPage(driver)
    success_page.navigate_to_international_contact_invest_success()
    assert 'Your form has been submitted.' in success_page.get_page()
