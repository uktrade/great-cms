from faker import Faker
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait

from tests.conftest import base_url

"""Parent for all pages"""
"""Contains generic methods for ALL pages"""


class TestHelper:
    def __init__(self, driver):
        self.driver = driver
        self._wait = WebDriverWait(self.driver, 4)
        self.base_url = base_url  # read this in dynamically based on target env
        self.fake = Faker()  # Generates valid fake data

    # these methods aren't exactly 100% necessary but allow us to control waits in one place instead of having
    # waits littered throughout and potentially compounding or controls/condenses more complex setup like Selects
    def navigate(self, url):
        self.driver.maximize_window()
        self.driver.get(url)

    def do_click(self, locator):
        self._wait.until(ec.visibility_of_element_located(locator)).click()

    def do_send_keys(self, locator, input_text):
        self._wait.until(ec.visibility_of_element_located(locator)).send_keys(input_text)

    def is_visible(self, locator):
        element = self._wait.until(ec.visibility_of_element_located(locator))
        return bool(element)

    def get_element_text(self, locator):
        element = self._wait.until(ec.visibility_of_element_located(locator))
        return element.text

    def do_select(self, locator, option):
        select_element = self._wait.until(ec.visibility_of_element_located(locator))
        select = Select(select_element)
        select.select_by_visible_text(option)

    def get_selected_option(self, locator):
        select_element = self._wait.until(ec.visibility_of_element_located(locator))
        select = Select(select_element)
        return select.all_selected_options[0].text
