import pytest

from international.forms import ContactForm, InternationalHCSATForm


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        (
            ContactForm,
            {
                'full_name': 'Jane Bloggs',
                'email': 'test@test.com',  # /PS-IGNORE
                'how_we_can_help': 'Please help me login',
            },
            True,
            {},
        ),
        (
            ContactForm,
            {
                'full_name': '',
                'email': '',
                'how_we_can_help': '',
            },
            False,
            {
                'email': ['Enter your email address'],
                'full_name': ['Enter your name'],
                'how_we_can_help': ['Enter information on what you were trying to do'],
            },
        ),
        (
            ContactForm,
            {
                'full_name': 'Joe Bloggs',
                'email': 'incorrect email',
                'how_we_can_help': 'Please help me login',
            },
            False,
            {'email': ['Enter an email address in the correct format, like name@example.com']},
        ),
        (
            ContactForm,
            {
                'full_name': 'Joe Bloggs',
                'email': 'test@test.com',
                'how_we_can_help': 'x' * 1001,
            },
            False,
            {
                'how_we_can_help': ['Information on what you were trying to do must be no more than 1,000 characters'],
            },
        ),
    ),
)
@pytest.mark.django_db
def test_contact_form_validation(form, form_data, form_is_valid, error_messages):
    form = form(data=form_data)
    assert form.is_valid() == form_is_valid
    assert error_messages == form.errors


@pytest.mark.parametrize(
    'form, form_data, form_is_valid, error_messages',
    (
        (
            InternationalHCSATForm,
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['NOT_FIND_LOOKING_FOR'],
                'experience_other': '',
                'likelihood_of_return': 'LIKELY',
                'service_specific_feedback': [],
                'service_specific_feedback_other': '',
                'service_improvements_feedback': 'This is some feedback',
            },
            True,
            {},
        ),
        (
            InternationalHCSATForm,
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['NOT_FIND_LOOKING_FOR'],
                'experience_other': '',
                'likelihood_of_return': 'LIKELY',
                'service_specific_feedback': [
                    'HELP_US_SET_UP_IN_THE_UK',
                    'UNDERSTAND_THE_UK_LEGAL_SYSTEM',
                    'PUT_US_IN_TOUCH_WITH_EXPERTS',
                ],
                'service_specific_feedback_other': '',
                'service_improvements_feedback': 'This is some feedback',
            },
            True,
            {},
        ),
        (
            InternationalHCSATForm,
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['NOT_FIND_LOOKING_FOR'],
                'experience_other': '',
                'likelihood_of_return': 'LIKELY',
                'service_specific_feedback': ['OTHER'],
                'service_specific_feedback_other': 'some other feedback',
                'service_improvements_feedback': 'This is some feedback',
            },
            True,
            {},
        ),
        (
            InternationalHCSATForm,
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['NOT_FIND_LOOKING_FOR'],
                'experience_other': '',
                'likelihood_of_return': 'LIKELY',
                'service_specific_feedback': ['OTHER'],
                'service_specific_feedback_other': '',
                'service_improvements_feedback': 'This is some feedback',
            },
            True,
            {},
        ),
        (
            InternationalHCSATForm,
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['NOT_FIND_LOOKING_FOR'],
                'experience_other': '',
                'likelihood_of_return': 'LIKELY',
                'service_specific_feedback': ['OTHER'],
                'service_specific_feedback_other': 'A' * 101,
                'service_improvements_feedback': 'This is some feedback',
            },
            False,
            {'service_specific_feedback_other': ['Ensure this value has at most 100 characters (it has 101).']},
        ),
    ),
)
@pytest.mark.django_db
def test_hcsat_user_feedback_form_validation(form, form_data, form_is_valid, error_messages):
    form = form(data=form_data)
    assert form.is_valid() == form_is_valid
    assert error_messages == form.errors
