import json

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


# read in from command line (or ide runner)
def pytest_addoption(parser):
    parser.addoption('--baseurl', '-U')
    parser.addoption('--browser', '-B', help='Options: chrome, firefox')
    parser.addoption('--headless', '-H', help='true or false')


# this will immediately get messy so will need extra functions to read in from config and perform
# https://docs.pytest.org/en/7.1.x/reference/reference.html?highlight=fixture#pytest.fixture
@pytest.fixture
def driver(request):
    selected_browser = select_browser(request)
    is_headless = assign_headless_request(request)
    driver = setup_driver_for_selected_browser(selected_browser, is_headless)
    yield driver
    driver.quit()
    """ TODO
    print(request.session.testsfailed)  # could be used to confirm test failure or log failures?
    # rerun failures? https://docs.pytest.org/en/7.1.x/how-to/cache.html#cache
    """


base_url = None


def pytest_configure(config):
    global base_url
    cli_request_url = config.getoption('--baseurl')
    if cli_request_url:
        base_url = cli_request_url
    else:
        base_url = get_config_from_json('baseurl')


def select_browser(request):
    if not request.config.getoption('--browser'):
        return get_config_from_json('browser')


def assign_headless_request(request):
    if not request.config.getoption('--headless'):
        return get_config_from_json('headless')


def setup_driver_for_selected_browser(selected_browser, is_headless):
    if selected_browser.strip().lower() == 'chrome':
        options = driver_options_setup(ChromeOptions(), is_headless)
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    elif selected_browser.strip().lower() == 'firefox':
        options = driver_options_setup(FirefoxOptions(), is_headless)
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)


def driver_options_setup(options, is_headless):
    options.add_argument('--incognito')
    if is_headless.strip().lower() == 'true':
        options.add_argument('--headless')
    return options


def get_config_from_json(config_name):
    with open('tests/ui/config.json') as f:
        return json.load(f)[config_name]
