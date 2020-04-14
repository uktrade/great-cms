import shutil

import pytest

from tests.browser.common_selectors import (
    HeaderCommon,
    LearnHowToExportFirstStepPage,
    LearnHowToExportPage,
)
from tests.browser.util import (
    attach_jpg_screenshot,
    find_element,
    selenium_action,
    should_not_see_errors,
    should_see_all_elements,
    try_alternative_click_on_exception,
)

pytestmark = [
    pytest.mark.browser,
    pytest.mark.learn_page,
    pytest.mark.django_db,
]


@pytest.mark.django_db
def test_can_get_to_learn_how_to_export_first_step_page(
    mock_dashboard_profile_events_opportunities,
    mock_export_plan_requests,
    first_step_page,
    server_user_browser_dashboard, single_event, single_opportunity
):

    live_server, user, browser = server_user_browser_dashboard
    should_not_see_errors(browser)
    attach_jpg_screenshot(browser, 'After submitting creds')

    with selenium_action(browser, 'Failed to click on Learning header link'):
        learn_link = find_element(browser, HeaderCommon.LEARNING)
        with try_alternative_click_on_exception(browser, learn_link):
            learn_link.click()

    attach_jpg_screenshot(browser, 'Learn How to Export page')
    should_see_all_elements(browser, LearnHowToExportPage)

    with selenium_action(browser, 'Failed to click on Learning header link'):
        learn_how_to_export_link = find_element(browser, LearnHowToExportPage.LEARN_HOW_TO_EXPORT)
        with try_alternative_click_on_exception(browser, learn_link):
            learn_how_to_export_link.click()

    attach_jpg_screenshot(browser, 'Learn How to Export - First Step page')
    should_see_all_elements(browser, LearnHowToExportFirstStepPage)
    should_see_all_elements(browser, LearnHowToExportFirstStepPage)
