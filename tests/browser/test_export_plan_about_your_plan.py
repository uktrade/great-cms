from unittest import mock

import pytest

from core import helpers
from tests.browser.common_selectors import (
    ExportPlanAboutYourBusiness,
    HeaderCommon,
    HeaderSignedIn,
    StickyHeader,
)
from tests.browser.util import should_not_see_errors, should_see_all_elements
from tests.helpers import create_response

pytestmark = pytest.mark.browser


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_dashboard_export_opportunities')
@mock.patch.object(helpers, 'get_dashboard_events')
@mock.patch.object(helpers, 'create_company_profile')
def test_export_plan_about_your_business(
    mock_create_company_profile, mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities, mock_get_company_profile,
    server_user_browser_dashboard
):

    def side_effect(_):
        mock_get_company_profile.return_value = {'foo': 'bar'}

    mock_create_company_profile.return_value = create_response()
    mock_create_company_profile.side_effect = side_effect
    mock_get_dashboard_events.return_value = []
    mock_get_dashboard_export_opportunities.return_value = []
    live_server, user, browser = server_user_browser_dashboard
    should_not_see_errors(browser)

    browser.get(live_server.url + '/export-plan/about-your-business/')
    should_see_all_elements(browser, HeaderCommon)
    should_see_all_elements(browser, HeaderSignedIn)
    should_see_all_elements(browser, StickyHeader)
    should_see_all_elements(browser, ExportPlanAboutYourBusiness)
