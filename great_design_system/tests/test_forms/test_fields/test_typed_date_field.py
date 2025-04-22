from datetime import datetime, timedelta

import pytest
from bs4 import BeautifulSoup

from great_design_system.forms import Form, TypedDateField


def get_day_month_year_from_datetime(dt):
    string = dt.strftime('%d/%m/%Y')
    return string.split('/')


def get_dates(defined_date, second_defined_date=None):
    day, month, year = get_day_month_year_from_datetime(defined_date)
    dates = {'defined_day': day, 'defined_month': month, 'defined_year': year}

    day, month, year = get_day_month_year_from_datetime(defined_date - timedelta(days=1))
    dates.update({'past_day': day, 'past_month': month, 'past_year': year})

    date = second_defined_date if second_defined_date else defined_date
    day, month, year = get_day_month_year_from_datetime(date + timedelta(days=1))
    dates.update({'future_day': day, 'future_month': month, 'future_year': year})

    return dates


today = datetime.today()
dates = get_dates(today)
threshold = today + timedelta(days=20)
threshold_end = today + timedelta(days=40)
thresholds = get_dates(threshold, threshold_end)

threshold_str = threshold.strftime('%d/%m/%Y')
threshold_end_str = threshold_end.strftime('%d/%m/%Y')

threshold_pstr = threshold.strftime('%d %b %Y')
threshold_end_pstr = threshold_end.strftime('%d %b %Y')


class TypedDateForm(Form):
    my_default_date = TypedDateField(required=True)
    my_past_and_today_date = TypedDateField(required=False, accept_future=False)
    my_future_and_today_date = TypedDateField(required=False, accept_past=False)
    my_past_date = TypedDateField(required=False, accept_future=False, accept_today=False)
    my_future_date = TypedDateField(required=False, accept_past=False, accept_today=False)
    my_accept_before_date_threshold_and_match = TypedDateField(
        required=False, date_thresholds=[threshold_str], accept_above_date_threshold=False
    )
    my_accept_above_date_threshold_and_match = TypedDateField(
        required=False, date_thresholds=[threshold_str], accept_before_date_threshold=False
    )
    my_accept_before_date_threshold = TypedDateField(
        required=False,
        date_thresholds=[threshold_str],
        accept_above_date_threshold=False,
        accept_match_date_threshold=False,
    )
    my_accept_above_date_threshold = TypedDateField(
        required=False,
        date_thresholds=[threshold_str],
        accept_before_date_threshold=False,
        accept_match_date_threshold=False,
    )
    my_threshold_with_start_and_end = TypedDateField(required=False, date_thresholds=[threshold_str, threshold_end_str])


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        # Test required
        (
            TypedDateForm,
            {
                'my_default_date_day': dates['defined_day'],
                'my_default_date_month': dates['defined_month'],
                'my_default_date_year': dates['defined_year'],
            },
            True,
            {},
        ),
        # Valid fields
        (
            TypedDateForm,
            {
                'my_default_date_day': dates['defined_day'],
                'my_default_date_month': dates['defined_month'],
                'my_default_date_year': dates['defined_year'],
                'my_past_and_today_date_day': dates['past_day'],
                'my_past_and_today_date_month': dates['past_month'],
                'my_past_and_today_date_year': dates['past_year'],
                'my_future_and_today_date_day': dates['future_day'],
                'my_future_and_today_date_month': dates['future_month'],
                'my_future_and_today_date_year': dates['future_year'],
                'my_past_date_day': dates['past_day'],
                'my_past_date_month': dates['past_month'],
                'my_past_date_year': dates['past_year'],
                'my_future_date_day': dates['future_day'],
                'my_future_date_month': dates['future_month'],
                'my_future_date_year': dates['future_year'],
                'my_accept_before_date_threshold_and_match_day': thresholds['past_day'],
                'my_accept_before_date_threshold_and_match_month': thresholds['past_month'],
                'my_accept_before_date_threshold_and_match_year': thresholds['past_year'],
                'my_accept_above_date_threshold_and_match_day': thresholds['future_day'],
                'my_accept_above_date_threshold_and_match_month': thresholds['future_month'],
                'my_accept_above_date_threshold_and_match_year': thresholds['future_year'],
                'my_accept_before_date_threshold_day': thresholds['past_day'],
                'my_accept_before_date_threshold_month': thresholds['past_month'],
                'my_accept_before_date_threshold_year': thresholds['past_year'],
                'my_accept_above_date_threshold_day': thresholds['future_day'],
                'my_accept_above_date_threshold_month': thresholds['future_month'],
                'my_accept_above_date_threshold_year': thresholds['future_year'],
                'my_threshold_with_start_and_end_day': thresholds['defined_day'],
                'my_threshold_with_start_and_end_month': thresholds['defined_month'],
                'my_threshold_with_start_and_end_year': thresholds['defined_year'],
            },
            True,
            {},
        ),
        # Dates in the past
        (
            TypedDateForm,
            {
                'my_default_date_day': dates['past_day'],
                'my_default_date_month': dates['past_month'],
                'my_default_date_year': dates['past_year'],
                'my_past_and_today_date_day': dates['past_day'],
                'my_past_and_today_date_month': dates['past_month'],
                'my_past_and_today_date_year': dates['past_year'],
                'my_future_and_today_date_day': dates['past_day'],
                'my_future_and_today_date_month': dates['past_month'],
                'my_future_and_today_date_year': dates['past_year'],
                'my_past_date_day': dates['past_day'],
                'my_past_date_month': dates['past_month'],
                'my_past_date_year': dates['past_year'],
                'my_future_date_day': dates['past_day'],
                'my_future_date_month': dates['past_month'],
                'my_future_date_year': dates['past_year'],
                'my_accept_before_date_threshold_and_match_day': thresholds['past_day'],
                'my_accept_before_date_threshold_and_match_month': thresholds['past_month'],
                'my_accept_before_date_threshold_and_match_year': thresholds['past_year'],
                'my_accept_above_date_threshold_and_match_day': thresholds['past_day'],
                'my_accept_above_date_threshold_and_match_month': thresholds['past_month'],
                'my_accept_above_date_threshold_and_match_year': thresholds['past_year'],
                'my_accept_before_date_threshold_day': thresholds['past_day'],
                'my_accept_before_date_threshold_month': thresholds['past_month'],
                'my_accept_before_date_threshold_year': thresholds['past_year'],
                'my_accept_above_date_threshold_day': thresholds['past_day'],
                'my_accept_above_date_threshold_month': thresholds['past_month'],
                'my_accept_above_date_threshold_year': thresholds['past_year'],
                'my_threshold_with_start_and_end_day': thresholds['past_day'],
                'my_threshold_with_start_and_end_month': thresholds['past_month'],
                'my_threshold_with_start_and_end_year': thresholds['past_year'],
            },
            False,
            {
                'my_future_and_today_date': ['My future and today date must be today or in the future.'],
                'my_future_date': ['My future date must be in the future.'],
                'my_accept_above_date_threshold_and_match': [
                    f'My accept above date threshold and match must be the same as or after {threshold_pstr}.'
                ],
                'my_accept_above_date_threshold': [f'My accept above date threshold must be after {threshold_pstr}.'],
                'my_threshold_with_start_and_end': [
                    f'My threshold with start and end must be between {threshold_pstr} and {threshold_end_pstr}.'
                ],
            },
        ),
        # Dates in the future
        (
            TypedDateForm,
            {
                'my_default_date_day': dates['future_day'],
                'my_default_date_month': dates['future_month'],
                'my_default_date_year': dates['future_year'],
                'my_past_and_today_date_day': dates['future_day'],
                'my_past_and_today_date_month': dates['future_month'],
                'my_past_and_today_date_year': dates['future_year'],
                'my_future_and_today_date_day': dates['future_day'],
                'my_future_and_today_date_month': dates['future_month'],
                'my_future_and_today_date_year': dates['future_year'],
                'my_past_date_day': dates['future_day'],
                'my_past_date_month': dates['future_month'],
                'my_past_date_year': dates['future_year'],
                'my_future_date_day': dates['future_day'],
                'my_future_date_month': dates['future_month'],
                'my_future_date_year': dates['future_year'],
                'my_accept_before_date_threshold_and_match_day': thresholds['future_day'],
                'my_accept_before_date_threshold_and_match_month': thresholds['future_month'],
                'my_accept_before_date_threshold_and_match_year': thresholds['future_year'],
                'my_accept_above_date_threshold_and_match_day': thresholds['future_day'],
                'my_accept_above_date_threshold_and_match_month': thresholds['future_month'],
                'my_accept_above_date_threshold_and_match_year': thresholds['future_year'],
                'my_accept_before_date_threshold_day': thresholds['future_day'],
                'my_accept_before_date_threshold_month': thresholds['future_month'],
                'my_accept_before_date_threshold_year': thresholds['future_year'],
                'my_accept_above_date_threshold_day': thresholds['future_day'],
                'my_accept_above_date_threshold_month': thresholds['future_month'],
                'my_accept_above_date_threshold_year': thresholds['future_year'],
                'my_threshold_with_start_and_end_day': thresholds['future_day'],
                'my_threshold_with_start_and_end_month': thresholds['future_month'],
                'my_threshold_with_start_and_end_year': thresholds['future_year'],
            },
            False,
            {
                'my_past_and_today_date': ['My past and today date must be today or in the past.'],
                'my_past_date': ['My past date must be in the past.'],
                'my_accept_before_date_threshold_and_match': [
                    f'My accept before date threshold and match must be the same as or before {threshold_pstr}.'
                ],
                'my_accept_before_date_threshold': [
                    f'My accept before date threshold must be before {threshold_pstr}.'
                ],
                'my_threshold_with_start_and_end': [
                    f'My threshold with start and end must be between {threshold_pstr} and {threshold_end_pstr}.'
                ],
            },
        ),
        # Defined date i.e. today() or date_thresholds['01/01/2025']
        (
            TypedDateForm,
            {
                'my_default_date_day': dates['defined_day'],
                'my_default_date_month': dates['defined_month'],
                'my_default_date_year': dates['defined_year'],
                'my_past_and_today_date_day': dates['defined_day'],
                'my_past_and_today_date_month': dates['defined_month'],
                'my_past_and_today_date_year': dates['defined_year'],
                'my_future_and_today_date_day': dates['defined_day'],
                'my_future_and_today_date_month': dates['defined_month'],
                'my_future_and_today_date_year': dates['defined_year'],
                'my_past_date_day': dates['defined_day'],
                'my_past_date_month': dates['defined_month'],
                'my_past_date_year': dates['defined_year'],
                'my_future_date_day': dates['defined_day'],
                'my_future_date_month': dates['defined_month'],
                'my_future_date_year': dates['defined_year'],
                'my_accept_before_date_threshold_and_match_day': thresholds['defined_day'],
                'my_accept_before_date_threshold_and_match_month': thresholds['defined_month'],
                'my_accept_before_date_threshold_and_match_year': thresholds['defined_year'],
                'my_accept_above_date_threshold_and_match_day': thresholds['defined_day'],
                'my_accept_above_date_threshold_and_match_month': thresholds['defined_month'],
                'my_accept_above_date_threshold_and_match_year': thresholds['defined_year'],
                'my_accept_before_date_threshold_day': thresholds['defined_day'],
                'my_accept_before_date_threshold_month': thresholds['defined_month'],
                'my_accept_before_date_threshold_year': thresholds['defined_year'],
                'my_accept_above_date_threshold_day': thresholds['defined_day'],
                'my_accept_above_date_threshold_month': thresholds['defined_month'],
                'my_accept_above_date_threshold_year': thresholds['defined_year'],
                'my_threshold_with_start_and_end_day': thresholds['defined_day'],
                'my_threshold_with_start_and_end_month': thresholds['defined_month'],
                'my_threshold_with_start_and_end_year': thresholds['defined_year'],
            },
            False,
            {
                'my_past_date': ['My past date must be in the past.'],
                'my_future_date': ['My future date must be in the future.'],
                'my_accept_before_date_threshold': [
                    f'My accept before date threshold must be before {threshold_pstr}.'
                ],
                'my_accept_above_date_threshold': [f'My accept above date threshold must be after {threshold_pstr}.'],
            },
        ),
    ),
)
@pytest.mark.django_db
def test_typed_date_field_with_valid_date(form, form_data, form_is_valid, error_messages):
    form = form(data=form_data)
    assert form.is_valid() == form_is_valid
    assert error_messages == form.errors


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        # blank required field
        (
            TypedDateForm,
            {},
            False,
            {'my_default_date': ['My default date must be a real date.']},
        ),
        # wrong formats
        (
            TypedDateForm,
            {
                'my_default_date_day': 'B',
                'my_default_date_month': 'A',
                'my_default_date_year': 'R',
            },
            False,
            {'my_default_date': ['My default date must be a real date.']},
        ),
        # wrong formats
        (
            TypedDateForm,
            {
                'my_default_date_day': '01',
                'my_default_date_month': '01',
                'my_default_date_year': '999',
            },
            False,
            {'my_default_date': ['My default date must be a real date.']},
        ),
        (
            TypedDateForm,
            {
                'my_default_date_day': '32',
                'my_default_date_month': '01',
                'my_default_date_year': '2000',
            },
            False,
            {'my_default_date': ['My default date must be a real date.']},
        ),
        (
            TypedDateForm,
            {
                'my_default_date_day': '01',
                'my_default_date_month': '13',
                'my_default_date_year': '2000',
            },
            False,
            {'my_default_date': ['My default date must be a real date.']},
        ),
        (
            TypedDateForm,
            {
                'my_default_date_day': '32',
                'my_default_date_month': '13',
                'my_default_date_year': '2000',
            },
            False,
            {'my_default_date': ['My default date must be a real date.']},
        ),
        (
            TypedDateForm,
            {
                'my_default_date_day': '32',
                'my_default_date_month': '13',
                'my_default_date_year': '20001',
            },
            False,
            {'my_default_date': ['My default date must be a real date.']},
        ),
        (
            TypedDateForm,
            {
                'my_default_date_day': '0',
                'my_default_date_month': '1',
                'my_default_date_year': '2000',
            },
            False,
            {'my_default_date': ['My default date must include a day.']},
        ),
        (
            TypedDateForm,
            {
                'my_default_date_day': '0',
                'my_default_date_month': '0',
                'my_default_date_year': '2000',
            },
            False,
            {'my_default_date': ['My default date must include a day and month.']},
        ),
        (
            TypedDateForm,
            {
                'my_default_date_day': '1',
                'my_default_date_month': '1',
                'my_default_date_year': '0',
            },
            False,
            {'my_default_date': ['Year must include 4 numbers.']},
        ),
    ),
)
@pytest.mark.django_db
def test_typed_date_field_with_invalid_date(form, form_data, form_is_valid, error_messages):
    form = form(data=form_data)
    assert form.is_valid() == form_is_valid
    assert error_messages == form.errors


def test_typed_date_field_form_render():

    html = open('./great_design_system/tests/test_forms/expected_html/typed_date_field.html', 'r')
    expected = html.read()
    actual = str(TypedDateForm())
    actual_stripped_html = BeautifulSoup(actual, 'html.parser').get_text(strip=True)
    expected_stripped_html = BeautifulSoup(expected, 'html.parser').get_text(strip=True)
    assert actual_stripped_html == expected_stripped_html

    # Close the file
    html.close()
