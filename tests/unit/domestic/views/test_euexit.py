from unittest import mock

import pytest
from django.urls import reverse

from contact.models import ContactPageContentSnippet, ContactSuccessSnippet
from core.constants import CONSENT_EMAIL
from core.snippet_slugs import EUEXIT_DOMESTIC_FORM, EUEXIT_FORM_SUCCESS
from domestic.views import euexit

pytestmark = pytest.mark.django_db


@pytest.fixture
def domestic_contact_form_snippets():
    # These will probably already exist from a data migration,
    # but handle if they are not present - eg running tests without migrations
    try:
        ContactPageContentSnippet.objects.get(
            slug=EUEXIT_DOMESTIC_FORM,
        )
    except ContactPageContentSnippet.DoesNotExist:
        snippet = ContactPageContentSnippet(
            slug=EUEXIT_DOMESTIC_FORM,
            internal_title='Transition Period form supporting content',
            breadcrumbs_label='Transition period enquiries',
            heading='Transition period enquiries',
            body_text=(
                '<p>See our guidance on <a href="https://www.gov.uk/transition">'
                "the transition period</a>. If you can't find the information you're "
                'looking for, complete the form below and one of our experts will try to help you.</p>'
            ),
            submit_button_text='Submit',
        )
        snippet.save()

    try:
        ContactSuccessSnippet.objects.get(
            slug=EUEXIT_FORM_SUCCESS,
        )
    except ContactSuccessSnippet.DoesNotExist:
        snippet = ContactSuccessSnippet(
            slug=EUEXIT_FORM_SUCCESS,
            internal_title='Transition Period form success page content',
            breadcrumbs_label='Transition period',
            heading='Thank you for submitting your question',
            body_text='We have sent you a confirmation email.',
            next_title='What happens next',
            next_body_text='We will review your question and get back to you.',
        )
        snippet.save()


def test_form_success_page(domestic_contact_form_snippets, settings, client):
    url = reverse('domestic:brexit-contact-form-success')
    template_name = euexit.DomesticContactSuccessView.template_name

    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == [template_name]
    snippet = response.context_data['content_snippet']
    for attrname, val in (
        ('breadcrumbs_label', 'Transition period'),
        ('heading', 'Thank you for submitting your question'),
        ('body_text', 'We have sent you a confirmation email.'),
        ('next_title', 'What happens next'),
        ('next_body_text', 'We will review your question and get back to you.'),
    ):
        assert getattr(snippet, attrname) == val


def test_domestic_form(domestic_contact_form_snippets, client):
    response = client.get(reverse('domestic:brexit-contact-form'))

    assert response.status_code == 200
    assert response.template_name == [euexit.DomesticContactFormView.template_name]


def test_domestic_form_no_snippets(domestic_contact_form_snippets, client, caplog):
    ContactPageContentSnippet.objects.filter(slug=EUEXIT_DOMESTIC_FORM).delete()
    ContactSuccessSnippet.objects.filter(slug=EUEXIT_FORM_SUCCESS).delete()
    url = reverse('domestic:brexit-contact-form')
    response = client.get(url)

    assert response.status_code == 404
    assert len(caplog.records) == 1
    assert caplog.records[0].message == 'Non-page CMS snippet is missing: see logged context. Raising 404.'
    assert caplog.records[0].levelname == 'ERROR'


@mock.patch.object(euexit.DomesticContactFormView.form_class, 'save')
def test_domestic_form_submit(mock_save, domestic_contact_form_snippets, settings, client, captcha_stub):
    settings.EU_EXIT_ZENDESK_SUBDOMAIN = 'brexit-subdomain'

    url = reverse('domestic:brexit-contact-form')

    # sets referrer in the session
    client.get(url, {}, HTTP_REFERER='http://www.google.com')
    response = client.post(
        url,
        {
            'first_name': 'test',
            'last_name': 'example',
            'email': 'test@example.com',
            'organisation_type': 'COMPANY',
            'company_name': 'thing',
            'comment': 'hello',
            'contact_consent': [CONSENT_EMAIL],
            'g-recaptcha-response': captcha_stub,
        },
    )

    assert response.status_code == 302
    assert response.url == reverse('domestic:brexit-contact-form-success')
    assert mock_save.call_count == 1
    assert mock_save.call_args == mock.call(
        subject='Brexit contact form',
        full_name='test example',
        email_address='test@example.com',
        service_name='eu_exit',
        subdomain=settings.EU_EXIT_ZENDESK_SUBDOMAIN,
        form_url=url,
        sender={'email_address': 'test@example.com', 'country_code': None, 'ip_address': None},
    )


def test_form_urls(domestic_contact_form_snippets, client, settings):
    url = reverse('domestic:brexit-contact-form')

    response = client.get(url, {}, HTTP_REFERER='http://www.google.com')

    assert response.status_code == 200
    form = response.context_data['form']
    assert form.ingress_url == 'http://www.google.com'


def test_form_url_no_referer(domestic_contact_form_snippets, settings, client):
    url = reverse('domestic:brexit-contact-form')

    response = client.get(url, {})

    assert response.status_code == 200
    form = response.context_data['form']
    assert form.ingress_url is None


def test_domestic_prepopulate(
    domestic_contact_form_snippets,
    client,
    user,
    mock_get_company_profile,
):
    mock_get_company_profile.return_value = {
        # Full spec of CompanySerializer is in
        # https://github.com/uktrade/directory-api/blob/master/company/serializers.py
        'name': 'Example corp',
        'postal_code': 'Foo Bar',
    }

    client.force_login(user)

    url = reverse('domestic:brexit-contact-form')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['form'].initial == {
        'email': user.email,
        'company_name': 'Example corp',
        'postcode': 'Foo Bar',
        'first_name': 'Jim',
        'last_name': 'Cross',
        'organisation_type': 'COMPANY',
    }
