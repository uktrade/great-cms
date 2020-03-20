from time import sleep
from unittest import mock

import pytest

from core import helpers
from tests.browser.common_selectors import (
    ExportPlanDashboard,
    ExportPlanDashboardPageTourStep0,
    ExportPlanDashboardPageTourStep1,
    ExportPlanDashboardPageTourStep2,
    ExportPlanDashboardPageTourStep3,
    ExportPlanDashboardPageTourStep4,
    ExportPlanDashboardPageTourStep5,
    HeaderCommon,
    HeaderSignedIn,
    StickyHeader,
)
from tests.browser.util import (
    attach_jpg_screenshot,
    find_element,
    should_not_see_element,
    should_not_see_errors,
    should_see_all_elements,
    try_alternative_click_on_exception,
)
from tests.helpers import create_response

pytestmark = pytest.mark.browser


def click_next(browser, step):
    next_button = find_element(browser, step.NEXT)
    with try_alternative_click_on_exception(browser, next_button):
        next_button.click()


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_dashboard_export_opportunities')
@mock.patch.object(helpers, 'get_dashboard_events')
@mock.patch.object(helpers, 'create_company_profile')
def test_export_plan_dashboard_without_page_tour(
    mock_create_company_profile, mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities, server_user_browser_dashboard,
):
    mock_create_company_profile.return_value = create_response()
    mock_get_dashboard_events.return_value = []
    mock_get_dashboard_export_opportunities.return_value = []
    live_server, user, browser = server_user_browser_dashboard
    should_not_see_errors(browser)

    browser.get(live_server.url + '/export-plan/dashboard/')

    should_see_all_elements(browser, HeaderCommon)
    should_see_all_elements(browser, HeaderSignedIn)
    should_see_all_elements(browser, StickyHeader)
    should_see_all_elements(browser, ExportPlanDashboard)


@pytest.mark.django_db
@mock.patch.object(helpers, 'get_dashboard_export_opportunities')
@mock.patch.object(helpers, 'get_dashboard_events')
@mock.patch.object(helpers, 'create_company_profile')
def test_export_plan_dashboard_with_page_tour(
    mock_create_company_profile, mock_get_dashboard_events,
    mock_get_dashboard_export_opportunities, server_user_browser_dashboard,
    mock_export_plan_dashboard_page_tours,
):
    mock_create_company_profile.return_value = create_response()
    mock_get_dashboard_events.return_value = []
    mock_get_dashboard_export_opportunities.return_value = []
    live_server, user, browser = server_user_browser_dashboard
    should_not_see_errors(browser)

    browser.get(live_server.url + '/export-plan/dashboard/')

    should_see_all_elements(browser, ExportPlanDashboardPageTourStep0)

    steps = [
        ExportPlanDashboardPageTourStep0,
        ExportPlanDashboardPageTourStep1,
        ExportPlanDashboardPageTourStep2,
        ExportPlanDashboardPageTourStep3,
        ExportPlanDashboardPageTourStep4,
        ExportPlanDashboardPageTourStep5,
    ]

    # click next for every step except the last one
    for idx, step in enumerate(steps[:-1]):
        click_next(browser, step)
        sleep(0.5)  # wait half a second for animation to end & get better screenshot
        attach_jpg_screenshot(browser, str(step))
        should_see_all_elements(browser, steps[idx+1])

    # click Start Now on the last tour step
    click_next(browser, ExportPlanDashboardPageTourStep5)
    should_not_see_element(browser, ExportPlanDashboardPageTourStep5.STEP)
