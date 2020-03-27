from unittest import mock
from urllib.parse import urljoin

import pytest

from core import helpers as core_helpers
from exportplan import helpers as exportplan_helpers
from django.urls import reverse
from tests.browser.common_selectors import (
    ExportPlanTargetMarketsData,
    ExportPlanTargetMarketsRecommendedCountriesFolded,
    ExportPlanTargetMarketsRecommendedCountriesUnfolded
)
from tests.browser.util import (
    attach_jpg_screenshot,
    should_not_see_errors,
    should_see_all_elements,
    selenium_action
)
from tests.helpers import create_response

pytestmark = [
    pytest.mark.browser,
    pytest.mark.export,
    pytest.mark.export_plan_dashboard,
]


@mock.patch.object(exportplan_helpers, 'get_comtrade_lastyearimportdata')
@mock.patch.object(exportplan_helpers, 'get_exportplan_rules_regulations')
@mock.patch.object(exportplan_helpers, 'get_exportplan_marketdata')
@mock.patch.object(core_helpers, 'get_dashboard_export_opportunities')
@mock.patch.object(core_helpers, 'get_dashboard_events')
@mock.patch.object(core_helpers, 'create_company_profile')
@mock.patch('core.helpers.store_user_location')
def test_can_see_target_markets_data(
    mock_user_location_create,
    mock_create_company_profile,
    mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities,
    mock_get_export_plan_market_data,
    mock_get_export_plan_rules_regulations,
    mock_get_comtrade_last_year_import_data,
    server_user_browser_dashboard,
    mock_export_plan_dashboard_page_tours,
):
    mock_create_company_profile.return_value = create_response()
    mock_get_dashboard_events.return_value = []
    mock_get_dashboard_export_opportunities.return_value = []

    mock_get_export_plan_rules_regulations.return_value = {
        'country': 'Australia',
        'commodity_code': '220.850',
    }
    mock_get_export_plan_market_data.return_value = {
        'timezone': 'Asia/Shanghai',
        'CPI': 10,
    }
    mock_get_comtrade_last_year_import_data.return_value = {
        'last_year_data_partner': {
            'Year': 2019,
            'value': 10000,
        }
    }

    live_server, user, browser = server_user_browser_dashboard
    should_not_see_errors(browser)

    target_markets_url = urljoin(live_server.url, reverse('exportplan:target-markets'))
    browser.get(target_markets_url)
    should_not_see_errors(browser)

    attach_jpg_screenshot(browser, 'market data with folded countries chooser')
    should_see_all_elements(browser, ExportPlanTargetMarketsData)
    should_see_all_elements(browser, ExportPlanTargetMarketsRecommendedCountriesFolded)

    sector_chooser_button = browser.find_element_by_id(
        ExportPlanTargetMarketsRecommendedCountriesFolded.SECTOR_CHOOSER_BUTTON.selector
    )
    with selenium_action(browser, f'Failed to mark lesson as read'):
        sector_chooser_button.click()
    attach_jpg_screenshot(browser, 'market data with unfolded countries chooser')
    should_see_all_elements(browser, ExportPlanTargetMarketsRecommendedCountriesUnfolded)
