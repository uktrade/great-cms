import pytest

from search.forms import FeedbackForm


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        (
            FeedbackForm,
            {
                'result_found': 'no',
                'search_target': 'Test',
                'contactable': 'no',
            },
            True,
            {},
        ),
        (
            FeedbackForm,
            {},
            False,
            {
                'contactable': 'This field is required.',
                'result_found': 'This field is required.',
                'search_target': 'This field is required.',
            },
        ),
    ),
)
@pytest.mark.django_db
def test_search_feedback_form_validation(form, form_data, form_is_valid, error_messages):
    form = form(data=form_data)
    assert form.is_valid() is form_is_valid
    if not form_is_valid:
        for key in error_messages:
            assert error_messages[key] in form.errors[key]