from conftest import base_url
from faker import Faker
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait

"""Parent for all pages"""
"""Contains generic methods for ALL pages"""


DESKTOP = 1
MOBILE_DEVICE = 2


class TestHelper:
    def __init__(self, driver):
        self.driver = driver
        self._wait = WebDriverWait(self.driver, 20)
        self.base_url = base_url  # read this in dynamically based on target env
        self.fake = Faker()  # Generates valid fake data
        self.driver.maximize_window()
        # comment above maximize_window and uncomment below for iPhone 12 Pro px size
        # self.driver.set_window_size(390, 844)
        self.device_type = self.get_device_type()

    def get_device_type(self):
        # breakpoint from core->sass->learn->_base.scss->$mobile
        mobile_breakpoint = 640
        window_size = self.driver.get_window_size()

        if window_size['width'] <= mobile_breakpoint:
            return MOBILE_DEVICE

        return DESKTOP

    # these methods aren't exactly 100% necessary but allow us to control waits in one place instead of having
    # waits littered throughout and potentially compounding or controls/condenses more complex setup like Selects
    def navigate(self, url):
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

    def find_element(self, locator):
        self._wait.until(ec.visibility_of_element_located(locator))
        element = self.driver.find_element(locator[0], locator[1])
        return element

    def find_elements(self, locator):
        self._wait.until(ec.visibility_of_element_located(locator))
        elements = self.driver.find_elements(locator[0], locator[1])
        return elements

    def do_select(self, locator, option):
        select_element = self._wait.until(ec.visibility_of_element_located(locator))
        select = Select(select_element)
        select.select_by_visible_text(option)

    def get_selected_option(self, locator):
        select_element = self._wait.until(ec.visibility_of_element_located(locator))
        select = Select(select_element)
        return select.all_selected_options[0].text

    def wait_for_url(self, url):
        return self._wait.until(ec.url_to_be(url))

    def wait_for_refresh(self, element):
        return self._wait.until(ec.staleness_of(element))
