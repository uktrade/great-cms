import pytest

from great_design_system.forms import EmailField, Form

REQUIRED_MESSAGE = 'This is my required message'
MAX_LENGTH = 320


class EmailFieldForm(Form):

    # Standard EmailField with TextInput widget
    my_required_email = EmailField()
    my_email = EmailField(required=False)
    my_required_email_with_required_error_message_override = EmailField(error_messages={'required': REQUIRED_MESSAGE})
    my_text_with_invalid_error_message = EmailField(
        required=False,
    )


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        (
            EmailFieldForm,
            {
                'my_required_email': 'dave@gmail.com',
                'my_required_email_with_required_error_message_override': 'dave@gmail.com',
            },
            True,
            {},
        ),
        (
            EmailFieldForm,
            {'my_email_with_invalid_error_message': 'a' * (MAX_LENGTH + 1)},
            False,
            {
                'my_required_email': ['This field is required.'],
                'my_required_email_with_required_error_message_override': [REQUIRED_MESSAGE],
            },
        ),
        (
            EmailFieldForm,
            {
                'my_required_email': 'foo',
                'my_required_email_with_required_error_message_override': 'bar',
            },
            False,
            {
                'my_required_email': ['Enter a valid email address.'],
                'my_required_email_with_required_error_message_override': ['Enter a valid email address.'],
            },
        ),
    ),
)
@pytest.mark.django_db
def test_email_field_with_valid_invalid_email_combinations(form, form_data, form_is_valid, error_messages):
    form = form(data=form_data)
    assert form.is_valid() == form_is_valid
    assert error_messages == form.errors
