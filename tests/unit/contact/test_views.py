from unittest import mock

import django.forms
import pytest
from django.conf import settings
from django.urls import reverse

from contact import constants, forms, views


@pytest.mark.parametrize(
    'url,success_url,view_class,subject,subdomain',
    (
        (
            reverse('contact:contact-us-domestic'),
            reverse('contact:contact-us-domestic-success'),
            views.DomesticFormView,
            settings.CONTACT_DOMESTIC_ZENDESK_SUBJECT,
            None,
        ),
        # TO BE PORTED IN SUBSEQUENT WORK
        # (
        #     reverse('contact-us-feedback'),
        #     reverse('contact-us-feedback-success'),
        #     views.FeedbackFormView,
        #     settings.CONTACT_DOMESTIC_ZENDESK_SUBJECT,
        #     None,
        # ),
        # (
        #     reverse('contact-us-exporting-to-the-trade-with-uk-app'),
        #     reverse('contact-us-international-success'),
        #     views.ExportingToUKFormView,
        #     settings.CONTACT_INTERNATIONAL_ZENDESK_SUBJECT,
        #     None,
        # ),
        # (
        #     reverse('contact-us-exporting-to-the-uk-import-controls'),
        #     reverse('contact-us-international-success'),
        #     views.ExportingToUKFormView,
        #     settings.CONTACT_INTERNATIONAL_ZENDESK_SUBJECT,
        #     settings.EU_EXIT_ZENDESK_SUBDOMAIN,
        # ),
        # (
        #     reverse('contact-us-exporting-to-the-uk-other'),
        #     reverse('contact-us-international-success'),
        #     views.ExportingToUKFormView,
        #     settings.CONTACT_INTERNATIONAL_ZENDESK_SUBJECT,
        #     settings.EU_EXIT_ZENDESK_SUBDOMAIN,
        # ),
    ),
)
@mock.patch.object(views.FormSessionMixin, 'form_session_class')
@pytest.mark.django_db
def test_zendesk_submit_success(mock_form_session, client, url, success_url, view_class, subject, settings, subdomain):
    class Form(forms.SerializeDataMixin, django.forms.Form):
        email = django.forms.EmailField()
        save = mock.Mock()
        full_name = 'Foo B'

    with mock.patch.object(view_class, 'form_class', Form):
        response = client.post(url, {'email': 'foo@bar.com'})

    assert response.status_code == 302
    assert response.url == success_url

    assert Form.save.call_count == 1
    assert Form.save.call_args == mock.call(
        email_address='foo@bar.com',
        form_session=mock_form_session(),
        form_url=url,
        full_name='Foo B',
        subject=subject,
        service_name=settings.DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME,
        sender={'email_address': 'foo@bar.com', 'country_code': None, 'ip_address': None},
        subdomain=subdomain,
    )


contact_urls_for_prefill_tests = (
    reverse('contact:contact-us-domestic'),  # DomesticFormView
    reverse('contact:contact-us-enquiries'),  # DomesticEnquiriesFormView
    # TO COME IN LATER WORK
    # reverse('contact-us-dso-form'),
    # reverse('contact-us-events-form'),
    # reverse('office-finder-contact', kwargs={'postcode': 'FOOBAR'}),
)


@pytest.mark.parametrize('url', contact_urls_for_prefill_tests)
@pytest.mark.django_db
@mock.patch('sso.models.get_or_create_export_plan')
def test_contact_us_short_form_prepopulated_when_logged_in(
    get_or_create_export_plan,
    client,
    url,
    user,
    mock_get_company_profile,
):
    client.force_login(user)  #  ensure the user is logged in

    get_or_create_export_plan.return_value = {}  # data is unnecessary here

    mock_get_company_profile.return_value = {
        # Full spec of CompanySerializer is in
        # https://github.com/uktrade/directory-api/blob/master/company/serializers.py
        'name': 'Example corp',
        'postal_code': 'Foo Bar',
    }

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['form'].initial == {
        'email': user.email,
        'company_type': constants.LIMITED,
        'organisation_name': 'Example corp',
        'postcode': 'Foo Bar',
        'family_name': 'Cross',
        'given_name': 'Jim',
    }


@pytest.mark.parametrize('url', contact_urls_for_prefill_tests)
@pytest.mark.django_db
def test_contact_us_short_form_not_prepopulated_if_logged_out(client, url, user):
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['form'].initial == {}
