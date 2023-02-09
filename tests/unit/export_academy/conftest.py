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
        'like_to_discuss': 'no',
        'how_can_we_help': 'buying a coffee',
        'terms_agreed': True,
    }
