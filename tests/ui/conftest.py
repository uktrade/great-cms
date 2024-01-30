import json
from typing import Dict

import pytest
from pytest import CollectReport, StashKey
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.remote.errorhandler import JavascriptException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


# read in from command line (or ide runner)
def pytest_addoption(parser):
    parser.addoption('--baseurl', '-U')
    parser.addoption('--browser', '-B', help='Options: chrome, firefox')
    parser.addoption('--headless', '-H', help='true or false')


phase_report_key = StashKey[Dict[str, CollectReport]]()


# @pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # store test results for each phase of a call, which can
    # be "setup", "call", "teardown"
    item.stash.setdefault(phase_report_key, {})[rep.when] = rep


@pytest.fixture(autouse=True)
def label_test_in_browserstack_console(request, driver):
    yield
    # request.node is an "item" because we use the default
    # "function" scope
    report = request.node.stash[phase_report_key]
    if report['setup'].failed:
        send_test_label(driver, 'failed', f"{report['call'].head_line} - Setup failed")
    elif ('call' not in report) or report['call'].failed:
        send_test_label(driver, 'failed', f"{report['call'].head_line} {report['call'].longrepr.reprcrash.message}")
    elif ('call' in report) and not report['call'].failed:
        send_test_label(driver, 'passed', f"{report['call'].head_line}")
    elif ('call' in report) and report['call'].skipped:
        send_test_label(driver, 'passed', f"Skipped - {report['call'].head_line}")


def send_test_label(driver, outcome, reason):
    try:
        executor_object = {
            'action': 'setSessionStatus',
            'arguments': {'status': outcome, 'reason': reason},
        }
        browserstack_executor = f'browserstack_executor: {json.dumps(executor_object)}'
        driver.execute_script(browserstack_executor)
    except JavascriptException:
        # this happens when we try and label tests that are not using browserstack-sdk. i.e. just pytest
        pass


# this will immediately get messy so will need extra functions to read in from config and perform
# https://docs.pytest.org/en/7.1.x/reference/reference.html?highlight=fixture#pytest.fixture
@pytest.fixture
def driver(request):
    js_disabled = False
    if hasattr(request, 'param') and type(request.param) is bool:
        js_disabled = request.param

    selected_browser = select_browser(request)
    is_headless = assign_headless_request(request)
    driver = setup_driver_for_selected_browser(selected_browser, is_headless, js_disabled)
    # driver.set_window_size(390, 844)
    yield driver
    driver.quit()
    """ TODO
    print(request.session.testsfailed)  # could be used to confirm test failure or log failures?
    # rerun failures? https://docs.pytest.org/en/7.1.x/how-to/cache.html#cache
    """


def get_config_from_json(config_name):
    with open('tests/ui/config.json') as f:
        return json.load(f)[config_name]


# default to config file as browserstack wasn't loading base_url via pytest_configure hook
base_url = get_config_from_json('baseurl')


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


def setup_driver_for_selected_browser(selected_browser, is_headless, js_disabled=False):
    if selected_browser.strip().lower() == 'chrome':
        options = driver_options_setup(ChromeOptions(), is_headless, js_disabled)
        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    elif selected_browser.strip().lower() == 'firefox':
        options = driver_options_setup(FirefoxOptions(), is_headless, js_disabled)
        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)


def driver_options_setup(options, is_headless, js_disabled=False):
    options.add_argument('--incognito')
    if is_headless.strip().lower() == 'true':
        options.add_argument('--headless')

    if js_disabled:
        options.add_experimental_option('prefs', {'profile.managed_default_content_settings.javascript': 2})

    return options
