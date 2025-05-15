import pytest

from international_investment_support_directory.forms import FindASpecialistContactForm


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'given_name': 'Joe',
                'family_name': 'Bloggs',
                'company_name': 'DBT',
                'country': 'FR',
                'email_address': 'joe.bloggs@businessandtrade.gov.uk',
                'sector': 'Food and drink',
                'subject': 'This is some dummy subject text',
                'body': 'This is some dummy body text',
                'terms': 'on',
                'marketing_consent': 'true',
            },
            True,
        ),
        (
            {
                'given_name': '',
                'family_name': '',
                'company_name': '',
                'country': '',
                'email_address': '',
                'sector': '',
                'subject': '',
                'body': '',
                'terms': '',
                'marketing_consent': '',
            },
            False,
        ),
        (
            {
                'given_name': 'Joe',
                'family_name': 'Bloggs',
                'company_name': 'DBT',
                'country': 'FR',
                'email_address': 'INVALID EMAIL ADDRESS FORMAT',
                'sector': 'Food and drink',
                'subject': 'This is some dummy subject text',
                'body': 'This is some dummy body text',
                'terms': 'true',
                'marketing_consent': 'true',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_investment_support_directory_contact_validation(form_data, is_valid):
    data = form_data
    form = FindASpecialistContactForm(data)
    print(dict(form.fields['sector'].choices))
    assert form.is_valid() == is_valid
