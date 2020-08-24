# -*- coding: utf-8 -*-
from typing import List
from unittest import mock
from uuid import uuid4

import pytest
from selenium.webdriver.remote.webdriver import WebDriver

import allure
from sso import helpers
from tests.browser.common_selectors import (
    HeaderSignedIn,
    SignUpModal,
    SignUpModalSuccess,
    SignUpModalVerificationCode,
)
from tests.browser.steps import (
    should_not_see_any_element,
    should_not_see_errors,
    should_see_all_elements,
)
from tests.helpers import create_response
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


@allure.step('Fill out and submit sign-up form')
def submit_sign_up_form(browser: WebDriver, email: str, password: str):
    email_input = find_element(browser, SignUpModal.EMAIL)
    password_input = find_element(browser, SignUpModal.PASSWORD)
    submit_button = find_element(browser, SignUpModal.SUBMIT)

    email_input.send_keys(email)
    password_input.send_keys(password)
    submit_button.click()


@allure.step('Submit verification code')
def submit_verification_code(browser: WebDriver, code: str):
    code_input = find_element(browser, SignUpModalVerificationCode.VERIFICATION_CODE)
    code_input.send_keys(code)

    submit_code = find_element(browser, SignUpModalVerificationCode.SUBMIT_CODE)
    submit_code.click()


@allure.step('Should not see errors during sign-up process')
def should_not_see_sign_up_errors(browser: WebDriver):
    error = 'Expected not to see sign-up errors'
    try:
        assert not is_element_present(browser, SignUpModal.ERROR_MESSAGES), error
    except AssertionError:
        attach_jpg_screenshot(browser, 'Unexpected error(s) during sign-up', selector=SignUpModal.MODAL)
        raise


@allure.step('Should see errors')
def should_see_expected_error_messages(
    browser: WebDriver, expected_email_errors: List[str], expected_password_errors: List[str]
):
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


@pytest.mark.parametrize(
    'email,password,expected_email_errors,expected_password_errors',
    [
        ('a@b.c', 'valid password', ['Enter a valid email address.'], []),
        (' ', 'valid password', ['This field may not be blank.'], []),
        ('a@b.cd', ' ', [], ['This field may not be blank.']),
        (
            'a@b.cd',
            'tooshort',
            [],
            [
                'This password is too short. It must contain at least 10 characters.',
                'This password contains letters only.',
            ],
        ),
        ('a@b.cd', 'onlyletters', [], ['This password contains letters only.']),
        (
            'a@b.cd',
            'password',
            [],
            [
                'This password is too short. It must contain at least 10 characters.',
                'This password is too common.',
                'This password contains letters only.',
                "This password contains the word 'password'",
            ],
        ),
        ('a@b.cd', '1234567890', [], ['This password is too common.', 'This password is entirely numeric.']),
    ],
)
@mock.patch.object(helpers, 'create_user')
def test_error_messages_for_invalid_credential(
    mock_create_user, browser, visit_signup_page, email, password, expected_email_errors, expected_password_errors,
):
    mock_create_user.side_effect = helpers.CreateUserException(
        detail={'email': expected_email_errors, 'password': expected_password_errors}, code=400
    )

    submit_sign_up_form(browser, email, password)

    should_see_expected_error_messages(browser, expected_email_errors, expected_password_errors)


@mock.patch.object(helpers, 'send_welcome_notification')
@mock.patch.object(helpers, 'check_verification_code')
@mock.patch.object(helpers, 'send_verification_code_email')
@mock.patch.object(helpers, 'create_user')
def test_users_should_be_able_to_sign_up(
    mock_create_user,
    mock_send_code,
    mock_verification,
    mock_notification,
    mock_user_location_create,
    browser,
    visit_signup_page,
):
    mock_verification.return_value = create_response()

    code = '12345'
    email = f'test+{uuid4()}@example.com'
    password = str(uuid4()).replace('-', '')
    mock_create_user.return_value = {'verification_code': code}

    submit_sign_up_form(browser, email, password)
    attach_jpg_screenshot(browser, 'After submitting valid credentials', selector=SignUpModal.MODAL)

    submit_verification_code(browser, code)
    should_not_see_sign_up_errors(browser)
    attach_jpg_screenshot(browser, 'After submitting code', selector=SignUpModal.MODAL)
    should_see_all_elements(browser, SignUpModalSuccess)
