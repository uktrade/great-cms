import pytest


@pytest.fixture
def valid_registration_form_data():
    return {
        'sector': 'Automotive',
        'job_title': 'Mechanic',
        'last_name': 'Bob',
        'first_name': 'Alice',
        'phone_number': '07777888999',
        'third_sector': '',
        'second_sector': '',
        'business_name': 'The MOT',
        'employee_count': '10 to 49',
        'export_product': 'Services',
        'annual_turnover': '£250,000 up to £499,999',
        'business_postcode': 'SW1 1AA',
        'export_experience': 'I have exported before but not in the last 12 months',
        'marketing_sources': 'Outdoor advertising digital screen',
    }


@pytest.fixture
def valid_registration_details_form_data():
    return {
        'first_name': 'Test name',
        'last_name': 'Test last',
        'job_title': 'Astronaut',
        'phone_number': '072345678910',
    }
