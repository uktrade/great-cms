import pytest
from learn.forms import CsatUserFeedbackForm


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['NOT_FIND_LOOKING_FOR'],
                'experience_other': '',
                'feedback_text': 'This is some feedback',
                'likelihood_of_return': 'LIKELY',
            },
            True,
        ),
        (
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['OTHER'],
                'experience_other': 'Something',
                'feedback_text': 'This is some feedback',
                'likelihood_of_return': 'LIKELY',
            },
            True,
        ),
        (
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['OTHER'],
                'experience_other': 'Something',
                'feedback_text': 'i' * 1300,
                'likelihood_of_return': 'LIKELY',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_csat_user_feedback_form_validation(form_data, is_valid):
    data = form_data
    form = CsatUserFeedbackForm(data)
    assert form.is_valid() == is_valid
