import pytest

from domestic_growth.forms import ScalingABusinessForm, StartingABusinessForm


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        (
            StartingABusinessForm,
            {
                'sector': 'Aerospace',
                'postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            True,
            {},
        ),
        (
            StartingABusinessForm,
            {
                'sector': '',
                'postcode': '',
            },
            False,
            {
                'sector': 'Select your sector',
                'postcode': 'Enter your postcode',
            },
        ),
    ),
)
@pytest.mark.django_db
def test_starting_a_business_form_validation(form, form_data, form_is_valid, error_messages):
    form = form(form_data)
    assert form.is_valid() is form_is_valid
    if not form_is_valid:
        for key in error_messages:
            assert error_messages[key] in form.errors[key]


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        (
            ScalingABusinessForm,
            {
                'country': 'uk',
                'sector': 'Aerospace',
                'business_stage': 'startup',
                'postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            True,
            {},
        ),
        (
            ScalingABusinessForm,
            {
                'country': '',
                'sector': '',
                'business_stage': '',
                'postcode': '',
            },
            False,
            {
                'country': 'Select your country',
                'sector': 'Select your sector',
                'business_stage': 'Select your stage of business',
                'postcode': 'Enter your postcode',
            },
        ),
    ),
)
@pytest.mark.django_db
def test_scaling_a_business_form_validation(form, form_data, form_is_valid, error_messages):
    form = form(form_data)
    assert form.is_valid() is form_is_valid
    if not form_is_valid:
        for key in error_messages:
            assert error_messages[key] in form.errors[key]
