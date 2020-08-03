# -*- coding: utf-8 -*-
from time import sleep

import pytest

import allure
from tests.browser.common_selectors import (
    ExportPlanDashboard,
    ExportPlanDashboardPageTourStep0,
    ExportPlanDashboardPageTourStep1,
    ExportPlanDashboardPageTourStep2,
    ExportPlanDashboardPageTourStep3,
    ExportPlanDashboardPageTourStep4,
    HeaderCommon,
    HeaderSignedIn,
    PersonalisationBar,
)
from tests.browser.steps import (
    should_not_see_element,
    should_see_all_elements,
    should_see_all_expected_page_sections,
    visit_page,
)
from tests.browser.util import (
    attach_jpg_screenshot,
    find_element,
    try_alternative_click_on_exception,
)

pytestmark = [
    pytest.mark.browser,
    pytest.mark.export_plan,
    pytest.mark.export_plan_dashboard,
]


@allure.step('Click on "Start Now/Next" button')
def click_next(browser, step):
    next_button = find_element(browser, step.NEXT)
    with try_alternative_click_on_exception(browser, next_button):
        next_button.click()


@allure.step('Click "Next" for every step except the last one')
def click_through_page_tour(browser):
    steps = [
        ExportPlanDashboardPageTourStep0,
        ExportPlanDashboardPageTourStep1,
        ExportPlanDashboardPageTourStep2,
        ExportPlanDashboardPageTourStep3,
        ExportPlanDashboardPageTourStep4,
    ]

    for idx, step in enumerate(steps[:-1]):
        click_next(browser, step)
        sleep(0.5)  # wait half a second for animation to end & get better screenshot
        attach_jpg_screenshot(browser, str(step))
        should_see_all_elements(browser, steps[idx + 1])

    click_next(browser, ExportPlanDashboardPageTourStep4)


@pytest.mark.django_db
def test_export_plan_dashboard_click_through_page_tour(
    server_user_browser_dashboard,
    mock_all_dashboard_and_export_plan_requests_and_responses,
    mock_get_company_profile_with_expertise
):
    live_server, user, browser = server_user_browser_dashboard

    visit_page(live_server, browser, '', 'Dashboard', endpoint='/export-plan/dashboard/')
    should_see_all_expected_page_sections(
        browser, [HeaderCommon, HeaderSignedIn, PersonalisationBar,
                  ExportPlanDashboard, ExportPlanDashboardPageTourStep0]
    )

    click_through_page_tour(browser)

    should_not_see_element(browser, ExportPlanDashboardPageTourStep4.STEP)
