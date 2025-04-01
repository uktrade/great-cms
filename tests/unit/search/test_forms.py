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
                'result_found': ['This field is required.'],
                'search_target': ['This field is required.'],
                'contactable': ['This field is required.'],
            },
        ),
        (
            FeedbackForm,
            {'result_found': 'no', 'search_target': 'Test', 'contactable': 'no', 'contact_email': 'bad email'},
            False,
            {
                'contact_email': [
                    'Enter a valid email address.',
                    'Enter an email address in the correct format, like name@example.com',
                ],
            },
        ),
        (
            FeedbackForm,
            {
                'result_found': 'no',
                'search_target': 'x' * 1001,
                'contactable': 'no',
            },
            False,
            {
                'search_target': ['Information on what you were searching for must be no more than 1,000 characters'],
            },
        ),
    ),
)
@pytest.mark.django_db
def test_search_feedback_form_validation(form, form_data, form_is_valid, error_messages):
    form = form(data=form_data)
    assert form.is_valid() is form_is_valid
    assert form.errors == error_messages
