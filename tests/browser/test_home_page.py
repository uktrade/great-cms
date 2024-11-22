# -*- coding: utf-8 -*-
import logging
from typing import List

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from tests.browser.common_selectors import (
    HeaderSignedIn,
    SignUpModal,
    SignUpModalVerificationCode,
)
from tests.browser.steps import should_not_see_any_element, should_not_see_errors
from tests.browser.util import (
    attach_jpg_screenshot,
    find_element,
    find_elements,
    is_element_present,
)

pytestmark = [
    pytest.mark.browser,
    pytest.mark.home_page,
    pytest.mark.django_db,
]

logger = logging.getLogger(__name__)


def submit_sign_up_form(browser: WebDriver, email: str, password: str):
    logger.info('Fill out and submit sign-up form')
    email_input = find_element(browser, SignUpModal.EMAIL)
    password_input = find_element(browser, SignUpModal.PASSWORD)
    submit_button = find_element(browser, SignUpModal.SUBMIT)

    email_input.send_keys(email)
    password_input.send_keys(password)
    submit_button.click()


def submit_verification_code(browser: WebDriver, code: str):
    logger.info('Submit verification code')
    code_input = find_element(browser, SignUpModalVerificationCode.VERIFICATION_CODE)
    code_input.send_keys(code)

    submit_code = find_element(browser, SignUpModalVerificationCode.SUBMIT_CODE)
    submit_code.click()


def should_not_see_sign_up_errors(browser: WebDriver):
    logger.info('Should not see errors during sign-up process')
    error = 'Expected not to see sign-up errors'
    try:
        assert not is_element_present(browser, SignUpModal.ERROR_MESSAGES), error
    except AssertionError:
        attach_jpg_screenshot(browser, 'Unexpected error(s) during sign-up', selector=SignUpModal.MODAL)
        raise


def should_see_expected_error_messages(
    browser: WebDriver, expected_email_errors: List[str], expected_password_errors: List[str]
):
    logger.info('Should see errors')
    attach_jpg_screenshot(browser, 'Sign-up modal with errors', selector=SignUpModal.MODAL)
    error_elements = find_elements(browser, SignUpModal.ERROR_MESSAGES)
    error_messages = [error.text for error in error_elements]
    for error in expected_email_errors:
        assert error in error_messages, f"Can't see expected email error: '{error}'"
    for error in expected_password_errors:
        assert error in error_messages, f"Can't see expected password error: '{error}'"


def test_anonymous_user_should_not_see_header_elements_for_authenticated_users(browser, visit_home_page):
    should_not_see_errors(browser)
    should_not_see_any_element(browser, HeaderSignedIn)
