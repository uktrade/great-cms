from selenium.webdriver.common.by import By

from pages.export_academy.base_ea_page import BaseEAPage


class LandingPage(BaseEAPage):
    def navigate_to_landing_page(self):
        self.navigate(f'{self.base_url}export-academy')

    def click_hero_register_button(self):
        hero_register_button = (By.LINK_TEXT, 'Register for an account')
        self.do_click(hero_register_button)

    def click_view_all_events_button(self):
        view_events_button = (By.LINK_TEXT, 'View all events')
        self.do_click(view_events_button)
