import pytest
from django.forms.forms import NON_FIELD_ERRORS

from find_a_buyer.forms import CsatUserFeedbackForm
from sso_profile.business_profile import forms, validators

pytestmark = pytest.mark.django_db


def test_description_form_contains_email():
    form = forms.DescriptionForm({'summary': 'contact foo@example.com', 'description': 'contact foo@example.com'})

    assert form.is_valid() is False
    assert form.errors == {
        'summary': [validators.MESSAGE_REMOVE_EMAIL],
        'description': [validators.MESSAGE_REMOVE_EMAIL],
    }


def test_case_study_rich_media_image_one_update_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_one': '123'})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[0]

    assert form['image_one'].label == expected_values['update_label']
    assert form['image_one'].help_text == (expected_values['update_help_text'].format(initial_value='123'))


def test_case_study_rich_media_image_one_create_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_one': None})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[0]

    assert form['image_one'].label == expected_values['create_label']
    assert form['image_one'].help_text == expected_values['create_help_text']


def test_case_study_rich_media_image_two_update_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_two': '123'})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[1]

    assert form['image_two'].label == expected_values['update_label']
    assert form['image_two'].help_text == (expected_values['update_help_text'].format(initial_value='123'))


def test_case_study_rich_media_image_two_create_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_two': None})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[1]

    assert form['image_two'].label == expected_values['create_label']
    assert form['image_two'].help_text == expected_values['create_help_text']


def test_case_study_rich_media_image_three_update_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_three': '123'})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[2]

    assert form['image_three'].label == expected_values['update_label']
    assert form['image_three'].help_text == (expected_values['update_help_text'].format(initial_value='123'))


def test_case_study_rich_media_image_three_create_help_text():
    form = forms.CaseStudyRichMediaForm(initial={'image_three': None})
    expected_values = forms.CaseStudyRichMediaForm.help_text_maps[2]

    assert form['image_three'].label == expected_values['create_label']
    assert form['image_three'].help_text == expected_values['create_help_text']


@pytest.mark.parametrize(
    'is_published,expected', ((True, forms.PublishForm.LABEL_UNPUBLISH_ISD), (False, forms.PublishForm.LABEL_ISD))
)
def test_label_is_published_investment_support_directory(is_published, expected):
    company = {'is_published_investment_support_directory': is_published}
    form = forms.PublishForm(company=company)
    field = form.fields['is_published_investment_support_directory']

    assert field.widget.label == expected


@pytest.mark.parametrize(
    'is_published,expected', ((True, forms.PublishForm.LABEL_UNPUBLISH_FAS), (False, forms.PublishForm.LABEL_FAS))
)
def test_label_is_published_find_a_supplier(is_published, expected):
    company = {'is_published_find_a_supplier': is_published}
    form = forms.PublishForm(company=company)
    field = form.fields['is_published_find_a_supplier']

    assert field.widget.label == expected


def test_companies_house_business_details_form():
    form = forms.CompaniesHouseBusinessDetailsForm(data={'sectors': 'MINING'})

    form.is_valid()
    assert form.cleaned_data['sectors'] == ['MINING']


def test_sole_trader_business_details_form():
    form = forms.NonCompaniesHouseBusinessDetailsForm(data={'sectors': 'MINING'})

    form.is_valid()
    assert form.cleaned_data['sectors'] == ['MINING']


def test_admin_invite_missing_email():
    form = forms.AdminInviteNewAdminForm(collaborator_choices=[], data={})

    assert form.is_valid() is False
    assert form.errors == {NON_FIELD_ERRORS: [form.MESSAGE_EMAIL_REQUIRED]}


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
