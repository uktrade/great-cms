from unittest import mock

import pytest

from core import helpers as core_helpers
from directory_api_client import api_client
from exportplan import helpers as exportplan_helpers
from tests.browser.common_selectors import (
    ExportPlanTargetMarkets,
    HeaderCommon,
    HeaderSignedIn,
    StickyHeader,
)
from tests.browser.util import should_not_see_errors, should_see_all_elements
from tests.helpers import create_response

pytestmark = [
    pytest.mark.browser,
    pytest.mark.export_plan,
    pytest.mark.export_plan_about_your_plan,
]


@pytest.mark.django_db
@mock.patch.object(exportplan_helpers, 'get_exportplan_marketdata')
@mock.patch.object(api_client.dataservices, 'get_lastyearimportdata')
@mock.patch.object(api_client.dataservices, 'get_corruption_perceptions_index')
@mock.patch.object(api_client.dataservices, 'get_easeofdoingbusiness')
@mock.patch.object(api_client.exportplan, 'exportplan_list')
@mock.patch.object(core_helpers, 'get_dashboard_export_opportunities')
@mock.patch.object(core_helpers, 'get_dashboard_events')
@mock.patch.object(core_helpers, 'update_company_profile')
def test_export_plan_about_your_business(
    mock_update_company_profile,
    mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities,
    mock_get_exportplan,
    mock_easeofdoingbusiness,
    mock_cpi,
    mock_lastyearimportdata,
    mock_get_exportplan_marketdata,
    server_user_browser_dashboard,
):
    mock_update_company_profile.return_value = create_response()
    mock_get_dashboard_events.return_value = []
    mock_get_dashboard_export_opportunities.return_value = []

    data = [
        {
            'export_countries': ['UK'],
            'export_commodity_codes': [100],
            'rules_regulations': {'rule1': 'AAA'}
        }
    ]
    mock_get_exportplan.return_value = create_response(data)

    easeofdoingbusiness_data = {
        'country_name': 'China',
        'country_code': 'CHN',
        'cpi_score_2019': 41,
        'rank': 80,
    }
    mock_easeofdoingbusiness.return_value = create_response(
        status_code=200, json_body=easeofdoingbusiness_data
    )

    cpi_data = {
        'country_name': 'China',
        'country_code': 'CHN',
        'cpi_score_2019': 41,
        'rank': 80,
    }
    mock_cpi.return_value = create_response(status_code=200, json_body=cpi_data)

    mock_lastyearimportdata.return_value = create_response(
        status_code=200, json_body={'lastyear_history': 123}
    )

    mock_get_exportplan_marketdata.return_value = {'timezone': 'Asia/Shanghai', }

    live_server, user, browser = server_user_browser_dashboard
    should_not_see_errors(browser)

    browser.get(live_server.url + '/export-plan/section/target-markets/')
    should_see_all_elements(browser, HeaderCommon)
    should_see_all_elements(browser, HeaderSignedIn)
    should_see_all_elements(browser, StickyHeader)
    should_see_all_elements(browser, ExportPlanTargetMarkets)
