import pytest

from core import forms
from core.cms_slugs import PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE
from core.forms import HCSATForm


def test_contact_us_form_empty_fields():
    form = forms.ContactUsHelpForm(
        data={
            'comment': '',
            'given_name': '',
            'family_name': '',
            'email': '',
            'terms_agreed': '',
        }
    )
    assert form.is_valid() is False
    assert form.errors == {
        'comment': ['This field is required.'],
        'given_name': ['This field is required.'],
        'family_name': ['This field is required.'],
        'email': ['This field is required.'],
        'terms_agreed': ['This field is required.'],
    }


def test_contact_us_form_non_empty_fields():
    data = {
        'comment': 'no comment',
        'given_name': 'First',
        'family_name': 'family',
        'email': 'test@test1234.com',
        'terms_agreed': True,
        'captcha': 'True',
    }
    form = forms.ContactUsHelpForm(data)
    assert form.is_valid()


def test_consent_field_mixin__privacy_url():
    instance = forms.ConsentFieldMixin()
    assert PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE in instance.fields['contact_consent'].label


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['NOT_FIND_LOOKING_FOR'],
                'experience_other': '',
                'service_improvements_feedback': 'This is some feedback',
                'likelihood_of_return': 'LIKELY',
            },
            True,
        ),
        (
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['OTHER'],
                'experience_other': 'Something',
                'service_improvements_feedback': 'This is some feedback',
                'likelihood_of_return': 'LIKELY',
            },
            True,
        ),
        (
            {
                'satisfaction': 'VERY_SATISFIED',
                'experience': ['OTHER'],
                'experience_other': 'Something',
                'service_improvements_feedback': 'i' * 1300,
                'likelihood_of_return': 'LIKELY',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_csat_user_feedback_form_validation(form_data, is_valid):
    data = form_data
    form = HCSATForm(data)
    assert form.is_valid() == is_valid
