import pytest

from international.forms import ContactForm


@pytest.mark.parametrize(
    'form_data,is_valid',
    (
        (
            {
                'full_name': 'Jane Bloggs',
                'email': 'test@test.com',
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
