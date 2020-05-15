# -*- coding: utf-8 -*-
import logging
import random
from typing import List
from unittest import mock

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

import allure
from exportplan import helpers as exportplan_helpers
from pytest_django.live_server_helper import LiveServer
from tests.browser.common_selectors import (
    ExportPlanTargetMarketsData,
    ExportPlanTargetMarketsDataTooltip,
    Selector,
    SelectorsEnum,
    TargetMarketsCountryChooser,
    TargetMarketsRecommendedCountries,
    TargetMarketsRecommendedCountriesFolded,
    TargetMarketsSectorSelectorUnfolded,
    TargetMarketsSectorsSelected,
    TargetMarketsSelectedSectors,
)
from tests.browser.conftest import CHINA, INDIA, JAPAN
from tests.browser.steps import (
    should_not_see_errors,
    should_see_all_elements,
    should_see_all_expected_page_sections,
    visit_page,
)
from tests.browser.util import (
    attach_jpg_screenshot,
    find_element,
    find_elements,
    scroll_to,
    selenium_action,
    wait_for_text_in_element,
)

logger = logging.getLogger(__name__)
pytestmark = [
    pytest.mark.browser,
    pytest.mark.export_plan,
    pytest.mark.target_markets,
]


@allure.step('Visit Target Markets page')
def visit_target_markets_page(live_server: LiveServer, browser: WebDriver):
    visit_page(live_server, browser, 'exportplan:target-markets', 'Target Markets')
    should_see_all_expected_page_sections(
        browser, [ExportPlanTargetMarketsData, TargetMarketsRecommendedCountriesFolded]
    )


@allure.step('Add sectors')
def add_sectors(browser: WebDriver) -> List[str]:
    add_sectors_button = browser.find_element_by_id(
        TargetMarketsRecommendedCountriesFolded.SECTOR_CHOOSER_BUTTON.selector
    )
    with selenium_action(browser, 'Failed to click on sector chooser button'):
        add_sectors_button.click()
    attach_jpg_screenshot(
        browser,
        'Recommended Countries component - Unfolded sector chooser',
        selector=TargetMarketsRecommendedCountriesFolded.CONTAINER,
    )
    should_see_all_elements(browser, TargetMarketsSectorSelectorUnfolded)

    sector_buttons = browser.find_elements_by_css_selector(TargetMarketsSectorSelectorUnfolded.SECTOR_BUTTONS.selector)
    random_sector_buttons = random.sample(sector_buttons, random.randint(1, 3))
    random_sector_names = [button.text for button in random_sector_buttons]

    for sector_button in random_sector_buttons:
        with selenium_action(browser, 'Failed to click on sector chooser button'):
            sector_button.click()
    attach_jpg_screenshot(
        browser,
        'Recommended Countries component - With selected sectors',
        selector=TargetMarketsRecommendedCountriesFolded.CONTAINER,
    )

    save_sectors_button = browser.find_element_by_id(TargetMarketsSectorsSelected.SAVE.selector)
    with selenium_action(browser, 'Failed to click on save sectors button'):
        save_sectors_button.click()
    attach_jpg_screenshot(
        browser,
        'Recommended Countries component - After saving selected sectors',
        selector=TargetMarketsRecommendedCountriesFolded.CONTAINER,
    )
    should_not_see_errors(browser)

    return random_sector_names


@allure.step('Should see selected sectors: {selected_sectors}')
def should_see_selected_sectors(browser: WebDriver, selected_sectors: List[str]):
    should_see_all_elements(browser, TargetMarketsSelectedSectors)
    visible_selected_sectors = browser.find_elements_by_css_selector(TargetMarketsSelectedSectors.SECTORS.selector)
    visible_sector_names = [sector_button.text for sector_button in visible_selected_sectors]
    attach_jpg_screenshot(
        browser, 'Selected sectors', selector=TargetMarketsRecommendedCountriesFolded.SECTOR_CHOOSER_SECTION
    )
    error = (
        f'Expected to see following sectors to be selected: {selected_sectors}, but '
        f'found {visible_sector_names} instead'
    )
    assert visible_sector_names == selected_sectors, error


@allure.step('Should see recommended countries')
def should_see_recommended_countries(browser: WebDriver):
    attach_jpg_screenshot(
        browser, 'Recommended countries section', selector=TargetMarketsRecommendedCountries.CONTAINER
    )
    should_see_all_elements(browser, TargetMarketsRecommendedCountries)


@allure.step('Add recommended {countries} to export plan')
def add_recommended_countries_to_export_plan(browser: WebDriver, countries: List[str]):
    recommended_countries = find_elements(browser, TargetMarketsRecommendedCountries.COUNTRY_BUTTONS)
    assert recommended_countries, 'No recommended countries found!'

    matching_country_buttons = []
    for button in recommended_countries:
        name = button.find_element_by_tag_name('figcaption').text
        if name in countries:
            matching_country_buttons.append((name, button))

    for name, button in matching_country_buttons:
        button_id = button.get_property('id')
        button_caption = Selector(By.CSS_SELECTOR, f'#{button_id} div.recommended-country__text')
        with wait_for_text_in_element(browser, button_caption, 'Selected'):
            button.click()
    should_see_recommended_countries(browser)


@allure.step('Should see target market data for following countries: {country_names}')
def should_see_target_market_data_for(browser: WebDriver, country_names: List[str]):
    attach_jpg_screenshot(
        browser, 'Recommended Countries component', selector=TargetMarketsRecommendedCountriesFolded.CONTAINER
    )
    visible_markets = browser.find_elements_by_css_selector(ExportPlanTargetMarketsData.MARKET_DATA.selector)
    visible_country_names = [market_data.find_element_by_tag_name('h2').text for market_data in visible_markets]
    for market_data in visible_markets:
        country = market_data.find_element_by_tag_name('h2').text
        attach_jpg_screenshot(browser, f'Market data for {country}', element=market_data)
    assert visible_country_names == country_names


@allure.step('Add {country} to the export plan')
def add_country_to_export_plan(browser: WebDriver, country: str):
    add_country_button = browser.find_element_by_id(ExportPlanTargetMarketsData.ADD_COUNTRY.selector)
    with selenium_action(browser, 'Failed to click on add country'):
        add_country_button.click()
    attach_jpg_screenshot(
        browser,
        'Recommended Countries component - after clicking on add country button',
        selector=TargetMarketsRecommendedCountriesFolded.CONTAINER,
    )

    country_input = browser.find_element_by_css_selector(TargetMarketsCountryChooser.COUNTRY_AUTOCOMPLETE_MENU.selector)
    with selenium_action(browser, 'Failed to click on add country'):
        country_input.click()

    country_elements = browser.find_elements_by_css_selector(
        TargetMarketsCountryChooser.AUTOCOMPLETE_COUNTRIES.selector
    )
    country_options = [element for element in country_elements if element.text == country]
    country_option = country_options[0]

    logger.info(f'Will select: {country_option}')
    with selenium_action(browser, 'Failed to select country'):
        country_option.click()

    save_country = browser.find_element_by_id(TargetMarketsCountryChooser.SAVE_COUNTRY.selector)
    with selenium_action(browser, 'Failed to click on save country'):
        save_country.click()
    attach_jpg_screenshot(
        browser,
        'Recommended Countries component - After saving country selection',
        selector=TargetMarketsRecommendedCountriesFolded.CONTAINER,
    )
    should_not_see_errors(browser)


def get_country_element(browser: WebDriver, tooltip_button: SelectorsEnum, country: str) -> WebElement:
    assert hasattr(tooltip_button, 'selector_template')
    selector_from_template = tooltip_button.selector_template.format(country=country.lower())
    new_selector = Selector(tooltip_button.by, selector_from_template)
    logger.info(
        f'Default selector "{tooltip_button.selector}" was replaced with country specific "{selector_from_template}"'
    )
    return find_element(browser, new_selector)


@allure.step('Show {tooltip_button} tooltip for {country} using mouse')
def show_tooltip_using_mouse(browser: WebDriver, tooltip_button: SelectorsEnum, country: str):
    button = get_country_element(browser, tooltip_button, country)
    scroll_to(browser, button)
    button.click()


@allure.step('Show {tooltip_button} tooltip for {country} using keyboard')
def show_tooltip_using_keyboard(browser: WebDriver, tooltip_button: SelectorsEnum, country: str):
    button = get_country_element(browser, tooltip_button, country)
    scroll_to(browser, button)
    button.send_keys(Keys.ENTER)


@allure.step('Should see {tooltip_selector} for {country}')
def should_see_ease_of_doing_business_tooltip(browser: WebDriver, tooltip_selector: SelectorsEnum, country: str):
    tooltip = get_country_element(browser, tooltip_selector, country)
    attach_jpg_screenshot(browser, 'tooltip')
    assert tooltip.is_displayed()
    assert tooltip.get_attribute('class').strip() != 'tooltip hidden'


@mock.patch.object(exportplan_helpers, 'update_exportplan')
def test_should_see_recommended_countries_for_selected_sectors(
    mock_update_exportplan, mock_all_dashboard_and_export_plan_requests_and_responses, server_user_browser_dashboard,
):
    updated_export_plan_data = {
        'pk': 1,
        'sectors': ['electrical'],
    }
    mock_update_exportplan.return_value = updated_export_plan_data
    live_server, user, browser = server_user_browser_dashboard

    visit_target_markets_page(live_server, browser)

    selected_sectors = add_sectors(browser)

    should_see_selected_sectors(browser, selected_sectors)
    should_see_recommended_countries(browser)


@mock.patch.object(exportplan_helpers, 'update_exportplan')
def test_can_add_multiple_recommended_countries(
    mock_update_exportplan, mock_all_dashboard_and_export_plan_requests_and_responses, server_user_browser_dashboard,
):
    get_export_plan_data_1 = {
        'pk': 1,
        'target_markets': [JAPAN],
    }
    get_export_plan_data_2 = {
        'pk': 1,
        'sectors': ['electrical'],
        'target_markets': [JAPAN, CHINA],
    }
    get_export_plan_data_3 = {
        'pk': 1,
        'sectors': ['electrical'],
        'target_markets': [JAPAN, CHINA, INDIA],
    }
    mock_update_exportplan.side_effect = [
        get_export_plan_data_1,
        get_export_plan_data_2,
        get_export_plan_data_3,
    ]
    live_server, user, browser = server_user_browser_dashboard

    visit_target_markets_page(live_server, browser)

    selected_sectors = add_sectors(browser)

    should_see_selected_sectors(browser, selected_sectors)
    should_see_recommended_countries(browser)

    add_recommended_countries_to_export_plan(browser, ['China', 'india'])

    should_see_target_market_data_for(browser, ['Japan', 'China', 'india'])


@mock.patch.object(exportplan_helpers, 'update_exportplan')
def test_can_add_multiple_countries_on_target_markets_page(
    mock_update_exportplan, mock_all_dashboard_and_export_plan_requests_and_responses, server_user_browser_dashboard,
):
    updated_export_plan_data = {
        'pk': 1,
        'target_markets': [JAPAN, CHINA],
    }
    mock_update_exportplan.return_value = updated_export_plan_data

    live_server, user, browser = server_user_browser_dashboard
    visit_target_markets_page(live_server, browser)
    should_see_target_market_data_for(browser, ['Japan'])

    add_country_to_export_plan(browser, 'China')

    should_see_target_market_data_for(browser, ['Japan', 'China'])


def test_should_see_tooltips_triggered_with_mouse(
    mock_all_dashboard_and_export_plan_requests_and_responses, server_user_browser_dashboard,
):
    live_server, user, browser = server_user_browser_dashboard
    visit_target_markets_page(live_server, browser)

    show_tooltip_using_mouse(browser, ExportPlanTargetMarketsDataTooltip.EASE_OF_DOING_BUSINESS_TOOLTIP_BUTTON, 'Japan')
    should_see_ease_of_doing_business_tooltip(
        browser, ExportPlanTargetMarketsDataTooltip.EASE_OF_DOING_BUSINESS_TOOLTIP, 'Japan'
    )

    show_tooltip_using_mouse(browser, ExportPlanTargetMarketsDataTooltip.CPI_TOOLTIP_BUTTON, 'Japan')
    should_see_ease_of_doing_business_tooltip(browser, ExportPlanTargetMarketsDataTooltip.CPI_TOOLTIP, 'Japan')


def test_should_see_tooltips_triggered_with_keyboard(
    mock_all_dashboard_and_export_plan_requests_and_responses, server_user_browser_dashboard,
):
    live_server, user, browser = server_user_browser_dashboard
    visit_target_markets_page(live_server, browser)

    show_tooltip_using_keyboard(
        browser, ExportPlanTargetMarketsDataTooltip.EASE_OF_DOING_BUSINESS_TOOLTIP_BUTTON, 'Japan'
    )
    should_see_ease_of_doing_business_tooltip(
        browser, ExportPlanTargetMarketsDataTooltip.EASE_OF_DOING_BUSINESS_TOOLTIP, 'Japan'
    )

    show_tooltip_using_keyboard(browser, ExportPlanTargetMarketsDataTooltip.CPI_TOOLTIP_BUTTON, 'Japan')
    should_see_ease_of_doing_business_tooltip(browser, ExportPlanTargetMarketsDataTooltip.CPI_TOOLTIP, 'Japan')


@mock.patch.object(exportplan_helpers, 'update_exportplan')
def test_should_see_tooltips_triggered_with_mouse_for_multiple_countries_on_target_markets_page(
    mock_update_exportplan, mock_all_dashboard_and_export_plan_requests_and_responses, server_user_browser_dashboard,
):
    updated_export_plan_data = {
        'pk': 1,
        'target_markets': [JAPAN, CHINA],
    }
    mock_update_exportplan.return_value = updated_export_plan_data

    live_server, user, browser = server_user_browser_dashboard
    visit_target_markets_page(live_server, browser)
    should_see_target_market_data_for(browser, ['Japan'])

    add_country_to_export_plan(browser, 'China')

    should_see_target_market_data_for(browser, ['Japan', 'China'])

    show_tooltip_using_mouse(browser, ExportPlanTargetMarketsDataTooltip.EASE_OF_DOING_BUSINESS_TOOLTIP_BUTTON, 'Japan')
    should_see_ease_of_doing_business_tooltip(
        browser, ExportPlanTargetMarketsDataTooltip.EASE_OF_DOING_BUSINESS_TOOLTIP, 'Japan'
    )
    show_tooltip_using_mouse(browser, ExportPlanTargetMarketsDataTooltip.CPI_TOOLTIP_BUTTON, 'Japan')
    should_see_ease_of_doing_business_tooltip(browser, ExportPlanTargetMarketsDataTooltip.CPI_TOOLTIP, 'Japan')

    show_tooltip_using_mouse(browser, ExportPlanTargetMarketsDataTooltip.EASE_OF_DOING_BUSINESS_TOOLTIP_BUTTON, 'China')
    should_see_ease_of_doing_business_tooltip(
        browser, ExportPlanTargetMarketsDataTooltip.EASE_OF_DOING_BUSINESS_TOOLTIP, 'China'
    )
    show_tooltip_using_mouse(browser, ExportPlanTargetMarketsDataTooltip.CPI_TOOLTIP_BUTTON, 'China')
    should_see_ease_of_doing_business_tooltip(browser, ExportPlanTargetMarketsDataTooltip.CPI_TOOLTIP, 'China')
