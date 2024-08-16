import pytest

from international_buy_from_the_uk.forms import ContactForm


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'given_name': 'Joe',
                'family_name': 'Bloggs',
                'email_address': 'joe.bloggs@businessandtrade.gov.uk',
                'phone_number': '07123456789',
                'sector': 'Advanced engineering',
                'organisation_name': 'DBT',
                'organisation_size': '1-10',
                'country': 'FR',
                'body': 'This is some test body data',
                'source': '',
                'source_other': '',
                'email_contact_consent': 'false',
                'telephone_contact_consent': 'false',
            },
            True,
        ),
        (
            {
                'given_name': '',
                'family_name': '',
                'email_address': '',
                'phone_number': '',
                'sector': '',
                'organisation_name': '',
                'organisation_size': '',
                'country': '',
                'body': '',
                'source': '',
                'source_other': '',
                'email_contact_consent': '',
                'telephone_contact_consent': '',
            },
            False,
        ),
    ),
)
@pytest.mark.django_db
def test_buy_from_the_uk_contact(mock_get_dbt_sectors, form_data, is_valid):
    data = form_data
    form = ContactForm(data)
    assert form.is_valid() == is_valid
