import random
from unittest import mock

import allure
import pytest
from selenium.webdriver.common.keys import Keys

from directory_constants import choices

from core import helpers
from tests.browser.common_selectors import DashboardModalLetsGetToKnowYou
from tests.browser.util import (
    attach_jpg_screenshot,
    find_element,
    should_not_see,
    should_see_all_elements,
)
from tests.helpers import create_response

pytestmark = pytest.mark.browser


@allure.step('Enter sectors user is interested in: {industries}')
def submit_industries(browser, industries):
    industries_input = find_element(
        browser, DashboardModalLetsGetToKnowYou.INDUSTRIES_INPUT
    )
    for industry in industries:
        industries_input.send_keys(industry)
        industries_input.send_keys(Keys.ENTER)

    attach_jpg_screenshot(
        browser,
        'After entering industries',
        selector=DashboardModalLetsGetToKnowYou.MODAL
    )

    continue_button = find_element(browser, DashboardModalLetsGetToKnowYou.SUBMIT)
    continue_button.click()


@pytest.mark.django_db
@mock.patch.object(helpers, 'create_company_profile')
def test_dashboard_forced_user(
    mock_create_company_profile, mock_get_company_profile, server_user_browser_dashboard
):
    def side_effect(_):
        mock_get_company_profile.return_value = {
            'expertise_countries': [],
            'expertise_industries': [],
        }

    mock_create_company_profile.return_value = create_response()
    mock_create_company_profile.side_effect = side_effect
    live_server, user, browser = server_user_browser_dashboard

    should_see_all_elements(browser, DashboardModalLetsGetToKnowYou)

    sector_labels = [label for _, label in choices.SECTORS]
    industries = random.sample(sector_labels, random.randint(1, 5))
    submit_industries(browser, industries)

    attach_jpg_screenshot(browser, 'Dashboard')
    should_not_see(browser, DashboardModalLetsGetToKnowYou)
