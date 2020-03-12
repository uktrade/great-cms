from unittest import mock

import pytest

from core import helpers as core_helpers
from directory_constants import choices
from sso import helpers as sso_helpers
from tests.browser.common_selectors import (
    DashboardModalLetsGetToKnowYou,
    HeaderSignedIn,
    MarketsContainer,
)
from tests.browser.util import (
    attach_jpg_screenshot,
    should_not_see,
    should_see_all_elements,
)

pytestmark = pytest.mark.browser


@pytest.mark.django_db
@mock.patch.object(sso_helpers, 'get_company_profile')
@mock.patch.object(core_helpers, 'get_markets_page_title')
def test_can_view_markets_as_signed_in_user(
    mock_get_markets_page_title, mock_get_company_profile, server_user_browser_dashboard
):
    mock_get_markets_page_title.return_value = 'Some page title'
    mock_get_company_profile.return_value = {
        'expertise_countries': ['AF'], 'expertise_industries': [choices.SECTORS[0][0]]
    }
    live_server, user, browser = server_user_browser_dashboard

    browser.get(live_server.url + "/markets/")

    attach_jpg_screenshot(browser, 'Markets')
    should_not_see(browser, DashboardModalLetsGetToKnowYou)
    should_see_all_elements(browser, HeaderSignedIn)
    should_see_all_elements(browser, MarketsContainer)
