import pytest
from bs4 import BeautifulSoup

from core.validators import is_valid_uk_postcode
from great_design_system.forms import CharField, Form

REQUIRED_MESSAGE = 'This is my required message'
INVALID_MESSAGE = 'This is my invalid message'
MAX_LENGTH = 100
MIN_LENGTH = 10


class CharFieldForm(Form):

    # Standard Charfield with TextInput widget
    my_required_text = CharField()
    my_text = CharField(required=False)
    my_required_text_with_required_error_message_override = CharField(error_messages={'required': REQUIRED_MESSAGE})
    my_text_with_invalid_error_message_override = CharField(
        required=False,
        max_length=MAX_LENGTH,
        min_length=MIN_LENGTH,
        error_messages={'max_length': INVALID_MESSAGE, 'min_length': INVALID_MESSAGE},
    )
    # Charfield with TextInput widget - With postcode validator
    my_text_with_postcode_validator = CharField(
        required=False,
        error_messages={'invalid': INVALID_MESSAGE},
        validators=[is_valid_uk_postcode],
    )


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        (
            CharFieldForm,
            {
                'my_required_text': 'foo',
                'my_required_text_with_required_error_message_override': 'bar',
            },
            True,
            {},
        ),
        (
            CharFieldForm,
            {'my_text_with_invalid_error_message_override': 'a' * (MAX_LENGTH + 1)},
            False,
            {
                'my_required_text': ['This field is required.'],
                'my_required_text_with_required_error_message_override': [REQUIRED_MESSAGE],
                'my_text_with_invalid_error_message_override': [INVALID_MESSAGE],
            },
        ),
        (
            CharFieldForm,
            {'my_text_with_invalid_error_message_override': 'a' * (MIN_LENGTH - 1)},
            False,
            {
                'my_required_text': ['This field is required.'],
                'my_required_text_with_required_error_message_override': [REQUIRED_MESSAGE],
                'my_text_with_invalid_error_message_override': [INVALID_MESSAGE],
            },
        ),
        (
            CharFieldForm,
            {
                'my_required_text': 'foo',
                'my_required_text_with_required_error_message_override': 'bar',
                'my_text_with_postcode_validator': 'bar',
            },
            False,
            {'my_text_with_postcode_validator': [INVALID_MESSAGE]},
        ),
        (
            CharFieldForm,
            {
                'my_required_text': 'foo',
                'my_required_text_with_required_error_message_override': 'bar',
                'my_text_with_postcode_validator': 'CB6 2NH',  # Valid postcode
            },
            True,
            {},
        ),
    ),
)
@pytest.mark.django_db
def test_char_field_with_valid_invalid_text_combinations(form, form_data, form_is_valid, error_messages):
    form = form(data=form_data)
    assert form.is_valid() == form_is_valid
    assert error_messages == form.errors


def test_char_field_form_render():

    expected = """
        <div class="govuk-error-summary great-hidden" data-module="govuk-error-summary">
            <div role="alert">
                <h2 class="govuk-error-summary__title">
                    There was a problem
                </h2>
                <div class="govuk-error-summary__body">
                    <p>
                        There was a problem with the form submission
                    </p>
                    <ul class="govuk-list govuk-error-summary__list"></ul>
                </div>
            </div>
        </div>
        <div class="govuk-form-group" id="id_my_required_text_container">
            <label class="govuk-label" for="id_my_required_text">
                My required text
            </label>
            <input class="govuk-input" id="id_my_required_text" name="my_required_text" type="text"/>
        </div>
        <div class="govuk-form-group" id="id_my_text_container">
            <label class="govuk-label" for="id_my_text">
                My text
            </label>
            <input class="govuk-input" id="id_my_text" name="my_text" type="text"/>
        </div>
        <div class="govuk-form-group" id="id_my_required_text_with_required_error_message_override_container">
            <label class="govuk-label" for="id_my_required_text_with_required_error_message_override">
                My required text with required error message override
            </label>
            <input class="govuk-input" id="id_my_required_text_with_required_error_message_override"
            name="my_required_text_with_required_error_message_override" type="text"/>
        </div>
        <div class="govuk-form-group" id="id_my_text_with_invalid_error_message_override_container">
            <label class="govuk-label" for="id_my_text_with_invalid_error_message_override">
                My text with invalid error message override
            </label>
            <input class="govuk-input" id="id_my_text_with_invalid_error_message_override"
            name="my_text_with_invalid_error_message_override" type="text"/>
        </div>
        <div class="govuk-form-group" id="id_my_text_with_postcode_validator_container">
            <label class="govuk-label" for="id_my_text_with_postcode_validator">
                My text with postcode validator
            </label>
            <input class="govuk-input" id="id_my_text_with_postcode_validator"
            name="my_text_with_postcode_validator" type="text"/>
        </div>
    """

    actual = str(CharFieldForm())

    actual_stripped_html = BeautifulSoup(actual, 'html.parser').get_text(strip=True)
    expected_stripped_html = BeautifulSoup(expected, 'html.parser').get_text(strip=True)

    assert actual_stripped_html == expected_stripped_html
