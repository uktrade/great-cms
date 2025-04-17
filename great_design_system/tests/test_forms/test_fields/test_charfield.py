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

    html = open('./great_design_system/tests/test_forms/expected_html/char_field.html', 'r')
    expected = html.read()
    actual = str(CharFieldForm())
    actual_stripped_html = BeautifulSoup(actual, 'html.parser').get_text(strip=True)
    expected_stripped_html = BeautifulSoup(expected, 'html.parser').get_text(strip=True)
    assert actual_stripped_html == expected_stripped_html

    # Close the file
    html.close()
