import pytest

from domestic.forms import (
    MarketAccessAboutForm,
    MarketAccessProblemDetailsForm,
    MarketAccessSummaryForm,
)

pytestmark = pytest.mark.django_db


@pytest.fixture
def about_form_data():
    business_type = 'I’m an exporter or investor, or ' 'I want to export or invest'
    return {
        'firstname': 'Craig',
        'lastname': 'Smith',
        'jobtitle': 'Musician',
        'business_type': business_type,
        'other_business_type': '',
        'company_name': 'Craig Music',
        'email': 'craig@craigmusic.com',
        'phone': '0123456789',
    }


@pytest.fixture
def about_form_data_with_other_business_type():
    return {
        'firstname': 'Craig',
        'lastname': 'Smith',
        'jobtitle': 'Musician',
        'business_type': 'Other',
        'other_business_type': 'Other business type',
        'company_name': 'Craig Music',
        'email': 'craig@craigmusic.com',
        'phone': '0123456789',
    }


def test_about_form_initial():
    form = MarketAccessAboutForm()
    assert form.fields['firstname'].initial is None
    assert form.fields['lastname'].initial is None
    assert form.fields['jobtitle'].initial is None
    assert form.fields['business_type'].initial is None
    assert form.fields['other_business_type'].initial is None
    assert form.fields['company_name'].initial is None
    assert form.fields['email'].initial is None
    assert form.fields['phone'].initial is None


def test_about_form_mandatory_fields():
    form = MarketAccessAboutForm(data={})

    assert form.fields['firstname'].required is True
    assert form.fields['lastname'].required is True
    assert form.fields['jobtitle'].required is True
    assert form.fields['business_type'].required is True
    assert form.fields['other_business_type'].required is False
    assert form.fields['company_name'].required is True
    assert form.fields['email'].required is True
    assert form.fields['phone'].required is True


def test_about_form_serialize(about_form_data):
    form = MarketAccessAboutForm(data=about_form_data)

    assert form.is_valid()
    assert form.cleaned_data == about_form_data


def test_about_form_with_other_serializes(about_form_data_with_other_business_type):
    form = MarketAccessAboutForm(data=about_form_data_with_other_business_type)

    assert form.is_valid()
    assert form.cleaned_data == about_form_data_with_other_business_type


def test_other_business_type_is_required_if_other_business_type(about_form_data_with_other_business_type):
    about_form_data_with_other_business_type['other_business_type'] = ''
    form = MarketAccessAboutForm(data=about_form_data_with_other_business_type)

    assert len(form.errors) == 1
    assert form.errors['other_business_type'] == ['Enter your organisation']


def test_about_form_error_messages():
    form = MarketAccessAboutForm(data={})

    assert len(form.errors) == 7
    form.errors['firstname'] == ['Enter your first name']
    form.errors['lastname'] == ['Enter your last name']
    form.errors['jobtitle'] == ['Enter your job title']
    form.errors['business_type'] == ['Enter your business type']
    form.errors['company_name'] == ['Enter your company name']
    form.errors['email'] == ['Enter your email']
    form.errors['phone'] == ['Enter your phone number']


@pytest.fixture
def problem_details_form_data():
    return {
        'product_service': 'something',
        'location': 'AO',
        'problem_summary': 'problem summary',
        'impact': 'problem impact',
        'resolve_summary': 'steps in resolving',
        'problem_cause': ['brexit'],
    }


def test_problem_details_form_initial():
    form = MarketAccessProblemDetailsForm()
    assert form.fields['product_service'].initial is None
    assert form.fields['location'].initial is None
    assert form.fields['problem_summary'].initial is None
    assert form.fields['impact'].initial is None
    assert form.fields['resolve_summary'].initial is None
    assert form.fields['problem_cause'].initial is None


def test_problem_details_form_mandatory_fields():
    form = MarketAccessProblemDetailsForm(data={})

    assert form.fields['product_service'].required is True
    assert form.fields['location'].required is True
    assert form.fields['problem_summary'].required is True
    assert form.fields['impact'].required is True
    assert form.fields['resolve_summary'].required is True
    assert form.fields['problem_cause'].required is False


def test_problem_details_form_serialize(problem_details_form_data):
    form = MarketAccessProblemDetailsForm(data=problem_details_form_data)
    assert form.is_valid()
    assert form.cleaned_data == {
        'location_label': 'Angola',
        'problem_cause_label': ['Brexit'],
        **problem_details_form_data,
    }


def test_problem_details_error_messages():
    form = MarketAccessProblemDetailsForm(data={})

    assert len(form.errors) == 5
    form.errors['product_service'] == ['Tell us what you’re trying to export or invest in']
    form.errors['location'] == ['Tell us where you are trying to export to or invest in']
    form.errors['problem_summary'] == ['Tell us about the problem you’re facing']
    form.errors['impact'] == ['Tell us how your business is being affected by the problem']
    form.errors['resolve_summary'] == [
        ('Tell us what you’ve done to resolve your problem, ' 'even if this is your first step')
    ]


def test_summary_form():
    form = MarketAccessSummaryForm(data={})

    assert form.fields['contact_by_email'].required is False
    assert form.fields['contact_by_phone'].required is False
