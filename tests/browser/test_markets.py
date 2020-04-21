# -*- coding: utf-8 -*-
import pytest

from tests.browser.common_selectors import (
    DashboardModalLetsGetToKnowYou,
    HeaderSignedIn,
    MarketsContainer,
)
from tests.browser.steps import (
    should_not_see_any_element,
    should_see_all_expected_page_sections,
    visit_page,
)

pytestmark = [
    pytest.mark.browser,
    pytest.mark.markets,
]


def test_can_view_markets_as_signed_in_user(server_user_browser_dashboard, mock_dashboard_profile_events_opportunities):
    live_server, user, browser = server_user_browser_dashboard

    visit_page(live_server, browser, 'core:markets', 'Markets')

    should_not_see_any_element(browser, DashboardModalLetsGetToKnowYou)
    should_see_all_expected_page_sections(browser, [HeaderSignedIn, MarketsContainer])
