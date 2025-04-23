import pytest

from domestic_growth.choices import LESS_THAN_3_YEARS_AGO
from domestic_growth.forms import (
    EmailGuideForm,
    ExistingBusinessCurrentlyExportForm,
    ExistingBusinessLocationForm,
    ExistingBusinessSectorForm,
    ExistingBusinessTurnoverForm,
    ExistingBusinessWhenSetUpForm,
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
            {'sector': "Enter your sector or industry and select the closest result, or select 'I don't know yet'"},
        ),
        (
            StartingABusinessSectorForm,
            {'sector': 'SL0003', 'dont_know_sector_yet': True},
            False,
            {
                'sector': "Enter your sector or industry and select the closest result, or select 'I don't know yet'"  # NOQA: E501
            },  # NOQA: E501
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
            {'postcode': 'Enter a full UK postcode'},
        ),
        (
            StartingABusinessLocationForm,
            {},
            False,
            {'postcode': 'Enter your postcode'},
        ),
        (
            ExistingBusinessSectorForm,
            {
                'sector': 'SL0003',
            },
            True,
            {},
        ),
        (
            ExistingBusinessSectorForm,
            {
                'cant_find_sector': True,
            },
            True,
            {},
        ),
        (
            ExistingBusinessSectorForm,
            {},
            False,
            {
                'sector': "Enter your sector or industry and select the closest result, or select 'I can't find my sector or industry'"  # NOQA: E501
            },  # NOQA: E501
        ),
        (
            ExistingBusinessSectorForm,
            {'sector': 'SL0003', 'cant_find_sector': True},
            False,
            {
                'sector': "Enter your sector or industry and select the closest result, or select 'I can't find my sector or industry'"  # NOQA: E501
            },  # NOQA: E501
        ),
        (
            ExistingBusinessLocationForm,
            {
                'postcode': 'BT809AQ',  # /PS-IGNORE
            },
            True,
            {},
        ),
        (
            ExistingBusinessLocationForm,
            {
                'postcode': 'BT80',  # /PS-IGNORE
            },
            False,
            {'postcode': 'Enter a full UK postcode'},
        ),
        (
            ExistingBusinessLocationForm,
            {},
            False,
            {'postcode': 'Enter your postcode'},
        ),
        (ExistingBusinessWhenSetUpForm, {'when_set_up': LESS_THAN_3_YEARS_AGO}, True, {}),
        (ExistingBusinessWhenSetUpForm, {}, False, {'when_set_up': 'Select when you set up your business'}),
        (ExistingBusinessTurnoverForm, {'turnover': '10M_PLUS'}, True, {}),
        (ExistingBusinessTurnoverForm, {'turnover': 'PREFER_NOT_TO_SAY'}, True, {}),
        (
            ExistingBusinessTurnoverForm,
            {},
            False,
            {'turnover': 'Select last financial year’s turnover, or select ‘Prefer not to say’'},
        ),
        (ExistingBusinessCurrentlyExportForm, {'currently_export': 'YES'}, True, {}),
        (
            ExistingBusinessCurrentlyExportForm,
            {},
            False,
            {'currently_export': 'Select if you currently export your products or services overseas'},
        ),
        (EmailGuideForm, {'email': 'test@example.com'}, True, {}),  # /PS-IGNORE
        (EmailGuideForm, {}, False, {'email': 'Enter an email address'}),
        (
            EmailGuideForm,
            {'email': 'example.com'},
            False,
            {'email': 'Enter an email address in the correct format, like name@example.com'},  # /PS-IGNORE
        ),
    ),
)
@pytest.mark.django_db
def test_domestic_growth_form_validation(mock_get_dbt_sectors, form, form_data, form_is_valid, error_messages):
    form = form(data=form_data)
    assert form.is_valid() is form_is_valid
    if not form_is_valid:
        for key in error_messages:
            assert error_messages[key] in form.errors[key]
