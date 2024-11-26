import pytest

from international.forms import ContactForm, InternationalHCSATForm


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'full_name': 'Jane Bloggs',
                'email': 'test@test.com',  # /PS-IGNORE
                'how_we_can_help': 'Please help me login',
            },
            True,
        ),
        (
            {
                'full_name': '',
                'email': '',
                'how_we_can_help': '',
            },
            False,
        ),
        (
            {
                'full_name': 'Joe Bloggs',
                'email': 'incorrect email',
                'how_we_can_help': 'Please help me login',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_contact_form_validation(form_data, is_valid):
    data = form_data
    form = ContactForm(data)
    assert form.is_valid() == is_valid


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
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
        ),
        (
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
        ),
        (
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
        ),
        (
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
        ),
        (
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
        ),
    ),
)
@pytest.mark.django_db
def test_hcsat_user_feedback_form_validation(form_data, is_valid):
    data = form_data
    form = InternationalHCSATForm(data)
    assert form.is_valid() == is_valid
