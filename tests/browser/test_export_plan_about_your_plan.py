# -*- coding: utf-8 -*-
import pytest

from tests.browser.steps import visit_page

pytestmark = [
    pytest.mark.browser,
    pytest.mark.export_plan,
    pytest.mark.export_plan_about_your_plan,
]


@pytest.mark.django_db
def test_export_plan_about_your_business_page(
    server_user_browser_dashboard, mock_all_dashboard_and_export_plan_requests_and_responses
):
    live_server, _, browser = server_user_browser_dashboard

    visit_page(live_server, browser, 'exportplan:about-your-business', 'about your business')
