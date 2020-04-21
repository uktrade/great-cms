# -*- coding: utf-8 -*-
import random
from unittest import mock

import pytest
from selenium.webdriver.common.keys import Keys

import allure
from core import helpers
from directory_constants import choices
from tests.browser.common_selectors import (
    DashboardContents,
    DashboardContentsOnSuccess,
    DashboardContentsWithoutSuccess,
    DashboardModalLetsGetToKnowYou,
    HeaderSignedIn,
)
from tests.browser.steps import should_not_see_any_element, should_see_all_elements
from tests.browser.util import (
    attach_jpg_screenshot,
    find_element,
    selenium_action,
    try_alternative_click_on_exception,
)
from tests.helpers import create_response

pytestmark = [
    pytest.mark.browser,
    pytest.mark.dashboard,
]


@allure.step('Enter sectors user is interested in: {industries}')
def submit_industries(browser, industries):
    industries_input = find_element(browser, DashboardModalLetsGetToKnowYou.INDUSTRIES_INPUT)
    for industry in industries:
        industries_input.send_keys(industry)
        industries_input.send_keys(Keys.ENTER)

    attach_jpg_screenshot(browser, 'After entering industries', selector=DashboardModalLetsGetToKnowYou.MODAL)

    with selenium_action(browser, 'Failed to submit industries'):
        continue_button = find_element(browser, DashboardModalLetsGetToKnowYou.SUBMIT)
        with try_alternative_click_on_exception(browser, continue_button):
            continue_button.click()


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_dashboard_export_opportunities')
@mock.patch.object(helpers, 'get_dashboard_events')
@mock.patch.object(helpers, 'update_company_profile')
def test_dashboard_with_success_query_parameter(
    mock_update_company_profile,
    mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities,
    mock_get_company_profile,
    server_user_browser_dashboard,
    single_event,
    single_opportunity,
):
    def side_effect(data, sso_session_id):
        mock_get_company_profile.return_value = {
            'expertise_countries': [],
            'expertise_industries': ['SL10001'],
        }

    mock_get_dashboard_events.return_value = create_response()
    mock_get_dashboard_events.side_effect = [[], [single_event], [single_event]]
    mock_get_dashboard_export_opportunities.return_value = create_response()
    mock_get_dashboard_export_opportunities.side_effect = [[], [single_opportunity], [single_opportunity]]
    mock_update_company_profile.return_value = create_response()
    mock_update_company_profile.side_effect = side_effect
    live_server, user, browser = server_user_browser_dashboard

    should_see_all_elements(browser, DashboardModalLetsGetToKnowYou)

    sector_labels = [label for _, label in choices.SECTORS]
    industries = random.sample(sector_labels, random.randint(1, 5))
    submit_industries(browser, industries)

    attach_jpg_screenshot(browser, 'Dashboard')
    should_not_see_any_element(browser, DashboardModalLetsGetToKnowYou)
    should_see_all_elements(browser, HeaderSignedIn)
    should_see_all_elements(browser, DashboardContents)
    should_see_all_elements(browser, DashboardContentsOnSuccess)


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_dashboard_export_opportunities')
@mock.patch.object(helpers, 'get_dashboard_events')
@mock.patch.object(helpers, 'update_company_profile')
def test_dashboard_without_success_query_parameter(
    mock_update_company_profile,
    mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities,
    mock_get_company_profile,
    server_user_browser_dashboard,
    single_event,
    single_opportunity,
):
    def side_effect(data, sso_session_id):
        mock_get_company_profile.return_value = {
            'expertise_countries': [],
            'expertise_industries': ['SL10001', 'SL10002'],
        }

    mock_get_dashboard_events.return_value = create_response()
    mock_get_dashboard_events.side_effect = [[], [single_event], [single_event]]
    mock_get_dashboard_export_opportunities.return_value = create_response()
    mock_get_dashboard_export_opportunities.side_effect = [[], [single_opportunity], [single_opportunity]]
    mock_update_company_profile.return_value = create_response()
    mock_update_company_profile.side_effect = side_effect
    live_server, user, browser = server_user_browser_dashboard

    should_see_all_elements(browser, DashboardModalLetsGetToKnowYou)

    sector_labels = [label for _, label in choices.SECTORS]
    industries = random.sample(sector_labels, random.randint(1, 5))
    submit_industries(browser, industries)

    attach_jpg_screenshot(browser, 'Dashboard with success query parameter')
    browser.get(f'{live_server.url}/dashboard/')
    attach_jpg_screenshot(browser, 'Dashboard without success query parameter')
    should_not_see_any_element(browser, DashboardModalLetsGetToKnowYou)
    should_see_all_elements(browser, HeaderSignedIn)
    should_see_all_elements(browser, DashboardContents)
    should_see_all_elements(browser, DashboardContentsWithoutSuccess)
