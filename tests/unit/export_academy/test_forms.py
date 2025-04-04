from datetime import datetime, timedelta

import pytest
from django.utils import timezone
from freezegun import freeze_time

from export_academy.forms import (
    BoolToDateTimeField,
    BusinessDetails,
    EventAdminModelForm,
    ExportExperience,
    MarketingSources,
    PersonalDetails,
    RegistrationConfirm,
)
from export_academy.models import Event


@pytest.mark.parametrize(
    'form, form_empty, error_messages',
    (
        (
            PersonalDetails(
                {
                    'first_name': 'Test name',
                    'last_name': 'Test last',
                    'job_title': 'Astronaut',
                    'phone_number': '072345678910',
                },
            ),
            PersonalDetails(
                {
                    'first_name': '',
                    'last_name': '',
                    'job_title': '',
                    'phone_number': '',
                },
            ),
            {
                'first_name': 'Enter your first name',
                'phone_number': 'Enter your telephone number',
                'last_name': 'Enter your last name',
                'job_title': 'Enter your job title',
            },
        ),
        (
            ExportExperience(
                {
                    'export_experience': 'I do not have a product for export',
                    'sector': 'Agriculture, horticulture, fisheries and pets',
                    'export_product': 'Goods',
                },
            ),
            ExportExperience(
                {
                    'export_experience': '',
                    'sector': '',
                    'export_product': '',
                },
            ),
            {
                'export_experience': 'Choose one option about your export experience',
                'sector': 'Choose a sector',
                'export_product': 'Choose one option about what you export',
            },
        ),
        (
            BusinessDetails(
                {
                    'business_name': 'Test Business',
                    'business_address_line_1': '1 Main Street',
                    'business_postcode': 'SW1A 1AA',
                    'annual_turnover': 'Up to £85,000',
                    'employee_count': '10 to 49',
                },
            ),
            BusinessDetails(
                {
                    'business_name': '',
                    'business_address_line_1': '',
                    'business_postcode': '',
                    'annual_turnover': '',
                    'employee_count': '',
                },
            ),
            {
                'business_name': 'Enter your business name',
                'business_address_line_1': 'Enter the first line of your business address',
                'business_postcode': 'Enter your business postcode',
                'annual_turnover': 'Enter a turnover amount',
                'employee_count': 'Choose number of employees',
            },
        ),
        (
            MarketingSources(
                {'marketing_sources': 'Other', 'marketing_sources_other': 'Friend of a friend'},
            ),
            MarketingSources(
                {
                    'marketing_sources': '',
                    'marketing_sources_other': '',
                },
            ),
            {
                'marketing_sources': 'Enter how you heard about the UK Export Academy',
                'marketing_sources_other': 'Enter how you heard about the UK Export Academy',
            },
        ),
        (
            RegistrationConfirm({'completed': datetime.now()}),
            RegistrationConfirm(),
            {},
        ),
    ),
)
@pytest.mark.django_db
def test_registration_form_validation(form, form_empty, error_messages):
    # Checks is_valid returns true for the given form data
    assert form.is_valid()

    if 'marketing_sources' in error_messages and form['marketing_sources'] != 'Other':
        pytest.skip('marketing_sources_other is an optional field if marketing_sources is not other')

    # Checks for the presence of each error message in the event of an invalid form
    for key in error_messages:
        assert not form_empty.is_valid()
        assert error_messages[key] in form_empty.errors[key]


@freeze_time('2023-01-01 01:00:00')
def test_custom_field_converts_boolean_to_datetime():
    field = BoolToDateTimeField()

    assert field.to_python(True) == timezone.now()
    assert field.to_python(False) is None


def test_event_admin_form_keeps_initial_values():
    EventAdminModelForm._meta.model = Event  # type: ignore
    EventAdminModelForm.formsets = {}  # type: ignore

    now = timezone.now()
    later = now + timedelta(hours=1)

    form = EventAdminModelForm()
    form['completed'].initial = now
    form['live'].initial = now
    form.cleaned_data = {'completed': later, 'live': later}

    assert form.clean_completed() == now
    assert form.clean_live() == now


def test_event_admin_form_keeps_new_values():
    EventAdminModelForm._meta.model = Event  # type: ignore
    EventAdminModelForm.formsets = {}  # type: ignore

    now = timezone.now()

    form = EventAdminModelForm()
    form['completed'].initial = None
    form['live'].initial = None
    form.cleaned_data = {'completed': now, 'live': now}

    assert form.clean_completed() == now
    assert form.clean_live() == now
