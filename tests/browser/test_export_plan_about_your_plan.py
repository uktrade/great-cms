# -*- coding: utf-8 -*-
import pytest

from tests.browser.common_selectors import (
    ExportPlanTargetMarkets,
    HeaderCommon,
    HeaderSignedIn,
    StickyHeader,
)
from tests.browser.steps import should_see_all_expected_page_sections, visit_page

pytestmark = [
    pytest.mark.browser,
    pytest.mark.export_plan,
    pytest.mark.export_plan_about_your_plan,
]


@pytest.mark.django_db
def test_export_plan_about_your_business(
    server_user_browser_dashboard,
    mock_update_company_profile,
    mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities,
    mock_get_export_plan_list,
    mock_get_corruption_perceptions_index,
    mock_get_ease_of_doing_business,
    mock_get_last_year_import_data,
    mock_get_export_plan_market_data,
    mock_get_recommended_countries,
    mock_update_export_plan,
):
    live_server, _, browser = server_user_browser_dashboard

    visit_page(live_server, browser, 'exportplan:target-markets', 'Target markets')

    should_see_all_expected_page_sections(
        browser, [HeaderCommon, HeaderSignedIn, StickyHeader, ExportPlanTargetMarkets]
    )
