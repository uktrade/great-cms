import pytest


@pytest.fixture
def valid_contact_form_data(captcha_stub):
    return {
        'full_name': 'Test name',
        'job_title': 'Astronaut',
        'email': 'test@test.com',
        'business_name': 'Limited',
        'business_website': 'limitedgoal.co.uk',
        'country': 'GB',
        'like_to_discuss': 'no',
        'how_can_we_help': 'buying a coffee',
        'terms_agreed': True,
        'g-recaptcha-response': captcha_stub,
    }


@pytest.fixture
def valid_contact_form_data_with_extra_options(captcha_stub):
    return {
        'full_name': 'Test name',
        'job_title': 'Astronaut',
        'email': 'test@test.com',
        'business_name': 'Limited',
        'business_website': 'limitedgoal.co.uk',
        'country': 'GB',
        'like_to_discuss': 'yes',
        'like_to_discuss_other': 'CN',
        'how_can_we_help': 'buying a coffee',
        'terms_agreed': True,
        'g-recaptcha-response': captcha_stub,
    }
