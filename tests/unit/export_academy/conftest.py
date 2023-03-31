from unittest import mock

import pytest


@pytest.fixture
def valid_registration_form_data():
    return {
        'first_name': 'Test name',
        'last_name': 'Test last',
        'job_title': 'Astronaut',
        'business_name': 'Limited',
        'business_website': 'limitedgoal.co.uk',
        'country': 'GB',
        'like_to_discuss': 'yes',
        'like_to_discuss_other': 'IT',
        'how_can_we_help': 'buying a coffee',
        'terms_agreed': True,
    }


@pytest.fixture
def patch_storage():
    with mock.patch('storages.backends.s3boto3.S3Boto3Storage') as a:
        yield a
