import pytest
from selenium.common.exceptions import TimeoutException

from pages.export_academy.landing_page import LandingPage


@pytest.fixture()
def landing_page(driver):
    landing_page = LandingPage(driver)
    landing_page.navigate_to_landing_page()
    try:
        landing_page.click_accept_cookies()
    except TimeoutException:
        # cookie modal only shown once in browserstack tests
        pass

    return landing_page


class TestLandingPageLoggedOut:
    def test_hero_cta_register_for_account(self, landing_page):
        landing_page.click_hero_register_button()
        assert landing_page.wait_for_url(
            'https://www.events.great.gov.uk/ereg/newreg.php?eventid=200236512&language=eng'
        )

    def test_breadcrumb_great(self, landing_page):
        landing_page.click_breadcrumb('great.gov.uk')
        assert landing_page.wait_for_url(f'{landing_page.base_url}')

    def test_essentials_card(self, landing_page):
        landing_page.click_card_link('card-essentials-link')
        assert landing_page.wait_for_url(f'{landing_page.base_url}export-academy/events/?type=essentials')

    def test_masterclasses_card(self, landing_page):
        landing_page.click_card_link('card-masterclasses-link')
        assert landing_page.wait_for_url(f'{landing_page.base_url}export-academy/events/?type=masterclass')

    def test_sector_markets_card(self, landing_page):
        landing_page.click_card_link('card-sector & market-link')
        assert landing_page.wait_for_url(f'{landing_page.base_url}export-academy/events/?type=sector&type=market')

    def test_view_events_button(self, landing_page):
        landing_page.click_view_all_events_button()
        assert landing_page.wait_for_url(f'{landing_page.base_url}export-academy/events/?')
