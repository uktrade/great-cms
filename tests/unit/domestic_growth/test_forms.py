import pytest

from domestic_growth.forms import (
    StartingABusinessLocationForm,
    StartingABusinessSectorForm,
)


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        (
            StartingABusinessSectorForm,
            {
                'sector': 'SL0003',
            },
            True,
            {},
        ),
        (
            StartingABusinessSectorForm,
            {
                'dont_know_sector_yet': True,
            },
            True,
            {},
        ),
        (
            StartingABusinessSectorForm,
            {},
            False,
            {'sector': "Enter your sector or industry and select the closest result, or select I don’t know yet"},
        ),
        (
            StartingABusinessLocationForm,
            {
                'postcode': 'BT809AQ',  # /PS-IGNORE
            },
            True,
            {},
        ),
        (
            StartingABusinessLocationForm,
            {
                'postcode': 'BT80',  # /PS-IGNORE
            },
            False,
            {'postcode': 'Enter a valid UK postcode'},
        ),
        (
            StartingABusinessLocationForm,
            {},
            False,
            {'postcode': 'Enter a full UK postcode'},
        ),
    ),
)
@pytest.mark.django_db
def test_starting_a_business_form_validation(mock_get_dbt_sectors, form, form_data, form_is_valid, error_messages):
    form = form(form_data)
    assert form.is_valid() is form_is_valid
    if not form_is_valid:
        for key in error_messages:
            assert error_messages[key] in form.errors[key]
