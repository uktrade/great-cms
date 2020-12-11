# -*- coding: utf-8 -*-

import allure
import pytest

from tests.browser.util import find_element, try_alternative_click_on_exception

pytestmark = [
    pytest.mark.browser,
    pytest.mark.export_plan,
    pytest.mark.export_plan_dashboard,
]


@allure.step('Click on "Start Now/Next" button')
def click_next(browser, step):
    next_button = find_element(browser, step.NEXT)
    with try_alternative_click_on_exception(browser, next_button):
        next_button.click()
