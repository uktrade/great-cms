from unittest import mock

import django.forms
import pytest
from directory_forms_api_client import actions
from django.conf import settings
from django.http import QueryDict
from django.urls import reverse
from requests.models import Response

from contact import constants, forms, helpers, views
from core import snippet_slugs
from core.cms_slugs import PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE
from core.constants import CONSENT_EMAIL
from core.tests.helpers import create_response

pytestmark = pytest.mark.django_db


locmem_cache_spec = {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    'LOCATION': 'contact-tests-unique-snowflake',
}


class FakeChoiceForm(django.forms.Form):
    choice = django.forms.CharField()


def build_wizard_url(step):
    return reverse('contact:contact-us-routing-form', kwargs={'step': step})


@pytest.fixture
def valid_request_export_support_form_data(captcha_stub):
    return {
        'first_name': 'Test',  # /PS-IGNORE
        'last_name': 'Name',  # /PS-IGNORE
        'email': 'test@test.com',  # /PS-IGNORE
        'phone_number': '+447501234567',
        'job_title': 'developer',
        'company_name': 'Limited',
        'company_postcode': 'sw1 1bb',  # /PS-IGNORE
        'employees_number': '1-9',
        'annual_turnover': '',
        'currently_export': 'no',
        'comment': 'some comment',
        'terms_agreed': True,
        'g-recaptcha-response': captcha_stub,
    }


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
        (
            reverse('contact:contact-us-feedback'),
            reverse('contact:contact-us-feedback-success'),
            views.FeedbackFormView,
            settings.CONTACT_DOMESTIC_ZENDESK_SUBJECT,
            None,
        ),
    ),
)
@mock.patch.object(views.FormSessionMixin, 'form_session_class')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_zendesk_submit_success(mock_form_session, client, url, success_url, view_class, subject, settings, subdomain):
    class Form(forms.SerializeDataMixin, django.forms.Form):
        email = django.forms.EmailField()
        save = mock.Mock()
        full_name = 'Foo B'

    with mock.patch.object(view_class, 'form_class', Form):
        response = client.post(url, {'email': 'foo@bar.com'})  # /PS-IGNORE

    assert response.status_code == 302
    assert response.url == success_url

    assert Form.save.call_count == 1
    assert Form.save.call_args == mock.call(
        email_address='foo@bar.com',  # /PS-IGNORE
        form_session=mock_form_session(),
        form_url=url,
        full_name='Foo B',
        subject=subject,
        service_name=settings.DIRECTORY_FORMS_API_ZENDESK_SEVICE_NAME,
        sender={'email_address': 'foo@bar.com', 'country_code': None, 'ip_address': None},  # /PS-IGNORE
        subdomain=subdomain,
    )


@pytest.mark.parametrize(
    'url,success_url,view_class,agent_template,user_template,agent_email',
    (
        (
            # V1 didn't have an explicit test for this
            reverse('contact:contact-us-enquiries'),
            reverse('contact:contact-us-domestic-success'),
            views.DomesticEnquiriesFormView,
            settings.CONTACT_ENQUIRIES_AGENT_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_ENQUIRIES_USER_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_ENQUIRIES_AGENT_EMAIL_ADDRESS,
        ),
        (
            reverse('contact:contact-us-events-form'),
            reverse('contact:contact-us-events-success'),
            views.EventsFormView,
            settings.CONTACT_EVENTS_AGENT_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_EVENTS_USER_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_EVENTS_AGENT_EMAIL_ADDRESS,
        ),
        (
            reverse('contact:contact-us-dso-form'),
            reverse('contact:contact-us-dso-success'),
            views.DefenceAndSecurityOrganisationFormView,
            settings.CONTACT_DSO_AGENT_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_DSO_USER_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_DSO_AGENT_EMAIL_ADDRESS,
        ),
    ),
)
@mock.patch.object(views.FormSessionMixin, 'form_session_class')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_notify_form_submit_success(
    mock_form_session,
    client,
    url,
    agent_template,
    user_template,
    view_class,
    agent_email,
    success_url,
    settings,
):
    class Form(forms.SerializeDataMixin, django.forms.Form):
        email = django.forms.EmailField()
        save = mock.Mock()

    with mock.patch.object(view_class, 'form_class', Form):
        response = client.post(url, {'email': 'test@example.com'})  # /PS-IGNORE

    assert response.status_code == 302
    assert response.url == success_url

    assert Form.save.call_count == 2
    assert Form.save.call_args_list == [
        mock.call(
            template_id=agent_template,
            email_address=agent_email,
            form_url=url,
            form_session=mock_form_session(),
            sender={
                'email_address': 'test@example.com',  # /PS-IGNORE
                'country_code': None,
                'ip_address': None,
            },
        ),
        mock.call(
            template_id=user_template,
            email_address='test@example.com',  # /PS-IGNORE
            form_url=url,
            form_session=mock_form_session(),
        ),
    ]


contact_urls_for_prefill_tests = (
    reverse('contact:contact-us-domestic'),
    reverse('contact:contact-us-enquiries'),
    reverse('contact:contact-us-dso-form'),
    reverse('contact:contact-us-events-form'),
)


@pytest.mark.parametrize('url', contact_urls_for_prefill_tests)
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_contact_us_short_form_prepopulated_when_logged_in(
    client,
    url,
    user,
    mock_get_company_profile,
):
    client.force_login(user)  # ensure the user is logged in

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
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_contact_us_short_form_not_prepopulated_if_logged_out(client, url, user):
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['form'].initial == {}


success_view_params = (
    reverse('contact:contact-us-domestic-success'),
    reverse('contact:contact-us-events-success'),
    reverse('contact:contact-us-dso-success'),
    reverse('contact:contact-us-feedback-success'),
    reverse('contact:contact-us-export-advice-success'),
)


@pytest.mark.parametrize('url', success_view_params)
@mock.patch.object(views.FormSessionMixin.form_session_class, 'clear')
@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_ingress_url_cleared_on_success(
    mock_get_snippet_instance,
    mock_clear,
    url,
    client,
):
    mock_clear.return_value = None
    # given the ingress url is set
    client.get(
        reverse('contact:contact-us-routing-form', kwargs={'step': 'location'}),
        HTTP_REFERER='http://testserver.com/foo/',
        HTTP_HOST='testserver.com',
    )

    # when the success page is viewed
    response = client.get(url, HTTP_HOST='testserver.com')

    # then the referer is exposed to the template
    assert response.context_data['next_url'] == 'http://testserver.com/foo/'
    assert response.status_code == 200
    # and the ingress url is cleared
    assert mock_clear.call_count == 1

    assert mock_get_snippet_instance.call_count == 1


@pytest.mark.parametrize('url', success_view_params)
@mock.patch.object(views.FormSessionMixin.form_session_class, 'clear')
@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_ingress_url_special_cases_on_success(
    mock_get_snippet_instance,
    mock_clear,
    url,
    client,
):
    mock_clear.return_value = None
    # /contact/<path> should always return to landing
    client.get(
        # TODO: replace URL name with contact:contact-us-routing-form with
        # kwargs={'step': 'location'} once that has been ported
        reverse('contact:contact-us-domestic'),
        HTTP_REFERER='http://testserver.com/contact/',
        HTTP_HOST='testserver.com',
    )
    response = client.get(url, HTTP_HOST='testserver.com')
    # for contact ingress urls user flow continues to homepage
    assert response.context_data['next_url'] == '/'
    assert response.status_code == 200
    # and the ingress url is cleared
    assert mock_clear.call_count == 1

    assert mock_get_snippet_instance.call_count == 1


@pytest.mark.parametrize('url', success_view_params)
@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
@mock.patch.object(views.FormSessionMixin.form_session_class, 'clear')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_external_ingress_url_not_used_on_success(
    mock_clear,
    mock_get_snippet_instance,
    url,
    client,
):
    mock_clear.return_value = None
    # given the ingress url is set
    client.get(
        reverse('contact:contact-us-routing-form', kwargs={'step': 'location'}),
        HTTP_REFERER='http://external.com/foo/',
        HTTP_HOST='testserver.com',
    )

    # when the success page is viewed
    response = client.get(url, HTTP_HOST='testserver.com')

    # then the referer is not exposed to the template
    assert response.context_data['next_url'] == '/'
    assert response.status_code == 200

    assert mock_get_snippet_instance.call_count == 1


@pytest.mark.parametrize('url', success_view_params)
@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
@mock.patch.object(views.FormSessionMixin.form_session_class, 'clear')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_ingress_url_not_set_on_success(
    mock_clear,
    mock_get_snippet_instance,
    url,
    client,
):
    mock_clear.return_value = None
    # when the success page is viewed and there is no referer set yet
    response = client.get(
        url,
        HTTP_HOST='testserver.com',
        HTTP_REFERER='http://testserver.com/foo/',
    )

    # then the referer is not exposed to the template
    assert response.context_data['next_url'] == '/'
    assert response.status_code == 200

    assert mock_get_snippet_instance.call_count == 1


@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_internal_ingress_url_used_on_first_step(client):
    # when an internal ingress url is set
    response = client.get(
        reverse('contact:contact-us-routing-form', kwargs={'step': 'location'}),
        HTTP_REFERER='http://testserver.com/foo/',
        HTTP_HOST='testserver.com',
    )

    # then the referer is exposed to the template
    assert response.context_data['prev_url'] == 'http://testserver.com/foo/'
    assert response.status_code == 200


@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_external_ingress_url_not_used_on_first_step(client):
    # when an external ingress url is set
    response = client.get(
        reverse('contact:contact-us-routing-form', kwargs={'step': 'location'}),
        HTTP_REFERER='http://external.com/foo/',
        HTTP_HOST='testserver.com',
    )

    # then the referer is not exposed to the template
    assert 'prev_url' not in response.context_data
    assert response.status_code == 200


@pytest.mark.parametrize(
    'current_step,choice',
    (
        (constants.DOMESTIC, constants.TRADE_OFFICE),
        (constants.INTERNATIONAL, constants.INVESTING),
        (constants.INTERNATIONAL, constants.BUYING),
    ),
)
@mock.patch.object(views.FormSessionMixin.form_session_class, 'clear')
def test_ingress_url_cleared_on_redirect_away(mock_clear, current_step, choice):
    mock_clear.return_value = None

    form = FakeChoiceForm(data={'choice': choice})

    view = views.RoutingFormView()
    view.steps = mock.Mock(current=current_step)
    view.storage = mock.Mock()
    view.url_name = 'contact:contact-us-routing-form'

    assert form.is_valid()


@mock.patch.object(views.EcommerceSupportFormPageView, 'form_session_class')
@mock.patch.object(views.EcommerceSupportFormPageView.form_class, 'save')
def test_ecommerce_export_form_notify_success(
    mock_save, mock_form_session, client, valid_request_export_support_form_data
):
    url = reverse('contact:ecommerce-export-support-form')
    response = client.post(url, valid_request_export_support_form_data)

    assert response.status_code == 302
    assert response.url == reverse('contact:ecommerce-export-support-success')
    assert mock_save.call_count == 2
    assert mock_save.call_args_list == [
        mock.call(
            email_address=settings.CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_EMAIL_ADDRESS,
            form_session=mock_form_session(),
            form_url=url,
            sender={
                'email_address': 'test@test.com',  # /PS-IGNORE
                'country_code': None,
                'ip_address': None,
            },
            template_id=settings.CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_NOTIFY_TEMPLATE_ID,
        ),
        mock.call(
            email_address='test@test.com',  # /PS-IGNORE
            form_session=mock_form_session(),
            form_url=url,
            template_id=settings.CONTACT_ECOMMERCE_EXPORT_SUPPORT_NOTIFY_TEMPLATE_ID,
        ),
    ]


def test_ecommerce_success_view(client):
    url = reverse('contact:ecommerce-export-support-success')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'current_step,choice,expected_url',
    (
        # location step routing
        (
            constants.LOCATION,
            constants.DOMESTIC,
            build_wizard_url(constants.DOMESTIC),
        ),
        (
            constants.LOCATION,
            constants.INTERNATIONAL,
            build_wizard_url(constants.INTERNATIONAL),
        ),
        (
            constants.DOMESTIC,
            constants.EXPORT_ADVICE,
            reverse('contact:contact-us-export-advice', kwargs={'step': 'comment'}),
        ),
        (
            constants.DOMESTIC,
            constants.FINANCE,
            reverse(
                'domestic:uk-export-finance-lead-generation-form',
                kwargs={'step': 'contact'},
            ),
        ),
        (
            constants.DOMESTIC,
            constants.EVENTS,
            reverse('contact:contact-us-events-form'),
        ),
        (
            constants.DOMESTIC,
            constants.DSO,
            reverse('contact:contact-us-dso-form'),
        ),
        (
            constants.DOMESTIC,
            constants.OTHER,
            reverse('contact:contact-us-enquiries'),
        ),
        # great services guidance routing
        (
            constants.GREAT_SERVICES,
            constants.EXPORT_OPPORTUNITIES,
            build_wizard_url(constants.EXPORT_OPPORTUNITIES),
        ),
        (
            constants.GREAT_SERVICES,
            constants.GREAT_ACCOUNT,
            build_wizard_url(constants.GREAT_ACCOUNT),
        ),
        (
            constants.GREAT_SERVICES,
            constants.OTHER,
            reverse('contact:contact-us-domestic'),
        ),
        # great account
        (
            constants.GREAT_ACCOUNT,
            constants.NO_VERIFICATION_EMAIL,
            helpers.build_account_guidance_url(snippet_slugs.HELP_MISSING_VERIFY_EMAIL),
        ),
        (
            constants.GREAT_ACCOUNT,
            constants.COMPANY_NOT_FOUND,
            helpers.build_account_guidance_url(snippet_slugs.HELP_ACCOUNT_COMPANY_NOT_FOUND),
        ),
        (
            constants.GREAT_ACCOUNT,
            constants.PASSWORD_RESET,
            helpers.build_account_guidance_url(snippet_slugs.HELP_PASSWORD_RESET),
        ),
        (
            constants.GREAT_ACCOUNT,
            constants.COMPANIES_HOUSE_LOGIN,
            helpers.build_account_guidance_url(snippet_slugs.HELP_COMPANIES_HOUSE_LOGIN),
        ),
        (
            constants.GREAT_ACCOUNT,
            constants.VERIFICATION_CODE,
            helpers.build_account_guidance_url(snippet_slugs.HELP_VERIFICATION_CODE_ENTER),
        ),
        (
            constants.GREAT_ACCOUNT,
            constants.NO_VERIFICATION_LETTER,
            helpers.build_account_guidance_url(snippet_slugs.HELP_VERIFICATION_CODE_LETTER),
        ),
        (
            constants.GREAT_ACCOUNT,
            constants.NO_VERIFICATION_MISSING,
            helpers.build_account_guidance_url(snippet_slugs.HELP_VERIFICATION_CODE_MISSING),
        ),
        (
            constants.GREAT_ACCOUNT,
            constants.OTHER,
            reverse('contact:contact-us-domestic'),
        ),
        # Export opportunities guidance routing
        (
            constants.EXPORT_OPPORTUNITIES,
            constants.NO_RESPONSE,
            helpers.build_export_opportunites_guidance_url(snippet_slugs.HELP_EXOPPS_NO_RESPONSE),
        ),
        (
            constants.EXPORT_OPPORTUNITIES,
            constants.ALERTS,
            helpers.build_export_opportunites_guidance_url(snippet_slugs.HELP_EXOPP_ALERTS_IRRELEVANT),
        ),
        (
            constants.EXPORT_OPPORTUNITIES,
            constants.OTHER,
            reverse('contact:contact-us-domestic'),
        ),
        # international routing has been removed: it's in great-international-ui
    ),
)
def test_render_next_step(current_step, choice, expected_url):
    form = FakeChoiceForm(data={'choice': choice})

    view = views.RoutingFormView()
    view.steps = mock.Mock(current=current_step)
    view.storage = mock.Mock()
    view.url_name = 'contact:contact-us-routing-form'
    view.request = mock.Mock()
    view.form_session = mock.Mock()

    assert form.is_valid()
    assert view.render_next_step(form).url == expected_url


@pytest.mark.parametrize(
    'current_step,expected_step',
    (
        (constants.DOMESTIC, constants.LOCATION),
        (constants.GREAT_SERVICES, constants.DOMESTIC),
        (constants.GREAT_ACCOUNT, constants.GREAT_SERVICES),
        (constants.EXPORT_OPPORTUNITIES, constants.GREAT_SERVICES),
    ),
)
def test_get_previous_step(current_step, expected_step):
    view = views.RoutingFormView()
    view.steps = mock.Mock(current=current_step)
    view.storage = mock.Mock()
    view.url_name = 'contact:contact-us-routing-form'

    assert view.get_prev_step() == expected_step


@pytest.mark.parametrize(
    'url,slug',
    (
        (
            reverse('contact:contact-us-events-success'),
            snippet_slugs.HELP_FORM_SUCCESS_EVENTS,
        ),
        (
            reverse('contact:contact-us-dso-success'),
            snippet_slugs.HELP_FORM_SUCCESS_DSO,
        ),
        (
            reverse('contact:contact-us-export-advice-success'),
            snippet_slugs.HELP_FORM_SUCCESS_EXPORT_ADVICE,
        ),
        (
            reverse('contact:contact-us-feedback-success'),
            snippet_slugs.HELP_FORM_SUCCESS_FEEDBACK,
        ),
        (
            reverse('contact:contact-us-domestic-success'),
            snippet_slugs.HELP_FORM_SUCCESS,
        ),
        (reverse('contact:contact-free-trade-agreements-success'), snippet_slugs.FTA_FORM_SUCCESS),
    ),
)
@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_success_view_cms_snippet_data(mock_get_snippet_instance, url, slug, client):
    response = client.get(url)

    assert response.status_code == 200
    mock_get_snippet_instance.assert_called_once()


@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_contact_us_feedback_prepopulate(
    client,
    user,
    mock_get_company_profile,
):
    client.force_login(user)  # ensure the user is logged in

    url = reverse('contact:contact-us-feedback')
    response = client.get(url)

    # Other forms try to pre-populate from the company info as well. This one does not
    assert not mock_get_company_profile.called

    assert response.status_code == 200
    assert response.context_data['form'].initial == {
        'email': user.email,
        'name': 'Jim Cross',
    }


@mock.patch('captcha.fields.ReCaptchaField.clean')
@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@mock.patch('directory_forms_api_client.actions.EmailAction')
@mock.patch('contact.helpers.retrieve_regional_office_email')
@mock.patch.object(views.FormSessionMixin, 'form_session_class')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_exporting_from_uk_contact_form_submission(
    mock_form_session,
    mock_retrieve_regional_office_email,
    mock_email_action,
    mock_notify_action,
    mock_clean,
    client,
    captcha_stub,
    company_profile,
    settings,
):
    company_profile.return_value = create_response(status_code=404)
    mock_retrieve_regional_office_email.return_value = 'regional@example.com'  # /PS-IGNORE

    url_name = 'contact:contact-us-export-advice'
    view_name = 'exporting_advice_form_view'

    response = client.post(
        reverse(url_name, kwargs={'step': 'comment'}),
        {
            view_name + '-current_step': 'comment',
            'comment-comment': 'some comment',
        },
    )
    assert response.status_code == 302

    response = client.post(
        reverse(url_name, kwargs={'step': 'personal'}),
        {
            view_name + '-current_step': 'personal',
            'personal-first_name': 'test',  # /PS-IGNORE
            'personal-last_name': 'test',  # /PS-IGNORE
            'personal-position': 'test',
            'personal-email': 'test@example.com',  # /PS-IGNORE
            'personal-phone': 'test',  # /PS-IGNORE
        },
    )

    assert response.status_code == 302

    response = client.post(
        reverse(url_name, kwargs={'step': 'business'}),
        {
            view_name + '-current_step': 'business',
            'business-company_type': 'LIMITED',
            'business-companies_house_number': '12345678',
            'business-organisation_name': 'Example corp',
            'business-postcode': '1234',
            'business-industry': 'Aerospace',
            'business-turnover': '0-25k',
            'business-employees': '1-10',
            'business-captcha': captcha_stub,
            'business-contact_consent': [CONSENT_EMAIL],
        },
    )
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 302
    assert response.url == reverse('contact:contact-us-domestic-success')
    assert mock_clean.call_count == 1
    assert mock_notify_action.call_count == 1
    assert mock_notify_action.call_args == mock.call(
        template_id=settings.CONTACT_EXPORTING_USER_NOTIFY_TEMPLATE_ID,
        email_address='test@example.com',  # /PS-IGNORE
        form_url='/contact/export-advice/comment/',
        form_session=mock_form_session(),
        email_reply_to_id=settings.CONTACT_EXPORTING_USER_REPLY_TO_EMAIL_ID,
    )
    assert mock_notify_action().save.call_count == 1
    assert mock_notify_action().save.call_args == mock.call(
        {
            'comment': 'some comment',
            'first_name': 'test',  # /PS-IGNORE
            'last_name': 'test',  # /PS-IGNORE
            'position': 'test',
            'email': 'test@example.com',  # /PS-IGNORE
            'phone': 'test',
            'company_type': 'LIMITED',
            'companies_house_number': '12345678',
            'company_type_other': '',
            'organisation_name': 'Example corp',
            'postcode': '1234',
            'industry': 'Aerospace',
            'industry_label': 'Aerospace',
            'industry_other': '',
            'turnover': '0-25k',
            'employees': '1-10',
            'region_office_email': 'regional@example.com',  # /PS-IGNORE
            'contact_consent': [CONSENT_EMAIL],
        }
    )

    assert mock_email_action.call_count == 1
    assert mock_email_action.call_args == mock.call(
        recipients=['regional@example.com'],  # /PS-IGNORE
        subject=settings.CONTACT_EXPORTING_AGENT_SUBJECT,
        reply_to=[settings.DEFAULT_FROM_EMAIL],
        form_url='/contact/export-advice/comment/',
        form_session=mock_form_session(),
        sender={'email_address': 'test@example.com', 'country_code': None, 'ip_address': None},  # /PS-IGNORE
    )
    assert mock_email_action().save.call_count == 1
    assert mock_email_action().save.call_args == mock.call({'text_body': mock.ANY, 'html_body': mock.ANY})

    assert mock_retrieve_regional_office_email.call_count == 1
    assert mock_retrieve_regional_office_email.call_args == mock.call('1234')


@mock.patch('captcha.fields.ReCaptchaField.clean')
@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@mock.patch('directory_forms_api_client.actions.EmailAction')
@mock.patch('contact.helpers.retrieve_regional_office_email')
@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_exporting_from_uk_contact_form_initial_data_business(
    mock_retrieve_regional_office_email,
    mock_email_action,
    mock_notify_action,
    mock_clean,
    client,
    captcha_stub,
    user,
    mock_get_company_profile,
):
    mock_get_company_profile.return_value = {
        # Full spec of CompanySerializer is in
        # https://github.com/uktrade/directory-api/blob/master/company/serializers.py
        'mobile_number': '55512345',
        'number': 1234567,
        'company_type': constants.LIMITED,
        'name': 'Example corp',
        'postal_code': 'Foo Bar',
        'sectors': [
            'AEROSPACE',
            'SOMETHING_ELSE_NOT_SHOWN',
        ],
        'employees': '1-10',
    }

    client.force_login(user)

    mock_retrieve_regional_office_email.return_value = 'regional@example.com'  # /PS-IGNORE

    url_name = 'contact:contact-us-export-advice'

    response_one = client.get(reverse(url_name, kwargs={'step': 'personal'}))

    assert response_one.context_data['form'].initial == {
        'email': user.email,
        'phone': '55512345',
        'first_name': 'Jim',
        'last_name': 'Cross',
    }

    response_two = client.get(reverse(url_name, kwargs={'step': 'business'}))

    assert response_two.context_data['form'].initial == {
        'company_type': constants.LIMITED,
        'companies_house_number': 1234567,
        'organisation_name': 'Example corp',
        'postcode': 'Foo Bar',
        'industry': 'AEROSPACE',
        'employees': '1-10',
    }


def test_marketing_join_form_notify_success(client, valid_request_export_support_form_data):
    url = reverse('contact:export-advice-routing-form')

    response = client.post(
        url,
        valid_request_export_support_form_data,
    )

    assert response.status_code == 302
    assert response.url == reverse(
        'contact:contact-us-export-advice',
        kwargs={
            'step': 'comment',
        },
    )


@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
def test_guidance_view_cms_retrieval(mock_get_snippet_instance, client):
    mock_snippet = mock.Mock()
    mock_snippet.body = '<p><b>test text here</b></p>'
    mock_get_snippet_instance.return_value = mock_snippet

    url = reverse(
        'contact:contact-us-export-opportunities-guidance',
        kwargs={'slug': 'the-slug'},
    )

    response = client.get(url)

    assert mock_snippet.body in response.content.decode('utf-8')

    assert response.status_code == 200
    assert mock_get_snippet_instance.call_count == 1


@mock.patch.object(views.FormSessionMixin, 'form_session_class')
def test_fta_form_submit_success(mock_form_session, client, settings):
    class Form(forms.SerializeDataMixin, django.forms.Form):
        email = django.forms.EmailField()
        save = mock.Mock()

        def __init__(self, *args, **kwargs):
            kwargs.pop('request', None)
            super().__init__(*args, **kwargs)

    with mock.patch.object(views.FTASubscribeFormView, 'form_class', Form):
        response = client.post(
            reverse('contact:contact-free-trade-agreements'), {'email': 'test@example.com'}  # /PS-IGNORE
        )

    assert response.status_code == 302
    assert response.url == reverse('contact:contact-free-trade-agreements-success')

    assert Form.save.call_count == 1
    assert Form.save.call_args_list == [
        mock.call(
            template_id=settings.SUBSCRIBE_TO_FTA_UPDATES_NOTIFY_TEMPLATE_ID,
            email_address='test@example.com',  # /PS-IGNORE
            form_url=reverse('contact:contact-free-trade-agreements'),
            form_session=mock_form_session(),
        ),
    ]


@pytest.mark.skipif(settings.FEATURE_DIGITAL_POINT_OF_ENTRY, reason='Redirect to new contact form')
def test_privacy_url_passed_to_fta_form_view(client, mock_free_trade_agreements):
    response = client.get(reverse('contact:contact-free-trade-agreements'))
    assert response.context['privacy_url'] == PRIVACY_POLICY_URL__CONTACT_TRIAGE_FORMS_SPECIAL_PAGE


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url,error_messages',
    (
        (
            reverse('contact:export-support'),
            {
                'business_type': 'limitedcompany',
                'business_name': 'Test business ltd',
                'business_postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            reverse('contact:export-support-step-2a'),
            {
                'business_type': 'Choose a business type',
                'business_name': 'Enter your business name',
                'business_postcode': 'Enter your business postcode',  # /PS-IGNORE
            },
        ),
        (
            reverse('contact:export-support'),
            {
                'business_type': 'other',
                'business_name': 'Test business ltd',
                'business_postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            reverse('contact:export-support-step-2b'),
            {
                'business_type': 'Choose a business type',
                'business_name': 'Enter your business name',
                'business_postcode': 'Enter your business postcode',  # /PS-IGNORE
            },
        ),
        (
            reverse('contact:export-support'),
            {
                'business_type': 'soletrader',
                'business_name': 'Test business ltd',
                'business_postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            reverse('contact:export-support-step-2c'),
            {
                'business_type': 'Choose a business type',
                'business_name': 'Enter your business name',
                'business_postcode': 'Enter your business postcode',
            },
        ),
        (
            reverse('contact:export-support-step-2a'),
            {
                'type': 'publiclimitedcompany',
                'annual_turnover': '<85k',
                'number_of_employees': '1-9',
                'sector_primary': 'Aerospace',
            },
            reverse('contact:export-support-step-3'),
            {
                'type': 'Choose a type of UK limited company',
                'annual_turnover': 'Please enter a turnover amount',
                'number_of_employees': 'Choose number of employees',
                'sector_primary': 'Choose a sector',
            },
        ),
        (
            reverse('contact:export-support-step-2b'),
            {
                'type': 'university',
                'annual_turnover': '<85k',
                'number_of_employees': '1-9',
                'sector_primary': 'Aerospace',
            },
            reverse('contact:export-support-step-3'),
            {
                'type': 'Choose a type of organisation',
                'annual_turnover': 'Please enter a turnover amount',
                'number_of_employees': 'Choose number of employees',
                'sector_primary': 'Choose a sector',
            },
        ),
        (
            reverse('contact:export-support-step-2c'),
            {
                'type': 'soletrader',
                'annual_turnover': '<85k',
                'sector_primary': 'Aerospace',
            },
            reverse('contact:export-support-step-3'),
            {
                'type': 'Choose a type of exporter',
                'annual_turnover': 'Please enter a turnover amount',
                'sector_primary': 'Choose a sector',
            },
        ),
        (
            reverse('contact:export-support-step-3'),
            {
                'first_name': 'Test',  # /PS-IGNORE
                'last_name': 'Name',  # /PS-IGNORE
                'job_title': 'Test job title',
                'uk_telephone_number': '07171771717',
                'email': 'name@example.com',  # /PS-IGNORE
            },
            reverse('contact:export-support-step-4'),
            {
                'first_name': 'Enter your first name',  # /PS-IGNORE
                'last_name': 'Enter your last name',  # /PS-IGNORE
                'job_title': 'Enter your job title',
                'uk_telephone_number': 'Enter your telephone number',  # /PS-IGNORE
                'email': 'Enter an email address in the correct format, like name@example.com',  # /PS-IGNORE
            },
        ),
        (
            reverse('contact:export-support-step-4'),
            {
                'product_or_service_1': 'Test product 1',
            },
            reverse('contact:export-support-step-5'),
            {
                'product_or_service_1': 'Enter a product or service',
            },
        ),
        (
            reverse('contact:export-support-step-5'),
            {
                'markets': ['AU'],
            },
            reverse('contact:export-support-step-6'),
            {
                'markets': 'Enter a market',
            },
        ),
        (
            reverse('contact:export-support-step-6'),
            {
                'about_your_experience': 'neverexported',
            },
            reverse('contact:export-support-step-7'),
            {
                'about_your_experience': 'Choose your export experience',
            },
        ),
        (
            reverse('contact:export-support-step-7'),
            {
                'received_support': 'yes',
                'contacted_gov_departments': 'no',
            },
            reverse('contact:export-support-step-8'),
            {
                'received_support': 'Choose an option',
                'contacted_gov_departments': 'Choose an option',
            },
        ),
    ),
)
@pytest.mark.django_db
@mock.patch('directory_forms_api_client.actions.ZendeskAction')
def test_domestic_export_support_form_pages(
    mock_action_class,
    page_url,
    form_data,
    redirect_url,
    error_messages,
    client,
    mock_site,
):
    invalid_form_data = form_data.copy()
    for key in form_data:
        invalid_form_data.pop(key)
        with mock.patch('wagtail.models.Site.find_for_request', return_value=mock_site):
            response = client.post(page_url, invalid_form_data)
        assert response.status_code == 200
        assert error_messages[key] in str(response.rendered_content)
        assert '<meta name="robots" content="noindex">' in str(response.rendered_content)

        invalid_form_data = form_data.copy()

    #   Redirect succeeds with valid data
    with mock.patch('wagtail.models.Site.find_for_request', return_value=mock_site):
        response = client.post(page_url, form_data)
    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url,error_messages',
    (
        (
            reverse('contact:export-support-step-8'),
            {
                'help_us_improve': 'satisfied',
            },
            reverse('contact:export-support-step-9'),
            {
                'help_us_improve': 'Choose an option',
            },
        ),
    ),
)
@mock.patch('directory_forms_api_client.actions.SaveOnlyInDatabaseAction')
@pytest.mark.django_db
def test_feedback_submit(mock_save_only_in_database_action, page_url, form_data, redirect_url, error_messages, client):
    response = client.post(
        page_url,
        form_data,
    )

    assert mock_save_only_in_database_action.call_count == 1
    assert response.status_code == 302
    assert response.url == redirect_url

    error_response = client.post(page_url, {})

    assert error_response.status_code == 200
    assert error_messages['help_us_improve'] in str(error_response.rendered_content)


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url,error_messages',
    (
        (
            reverse('contact:export-support-edit'),
            {
                'business_type': 'soletrader',  # /PS-IGNORE
                'business_name': 'Test business ltd',  # /PS-IGNORE
                'business_postcode': 'SW1A 1AA',  # /PS-IGNORE
            },
            reverse('contact:export-support-step-7'),
            {
                'business_type': 'Choose a business type',
                'business_name': 'Enter your business name',
                'business_postcode': 'Enter your business postcode',
            },
        ),
        (
            reverse('contact:export-support-step-2a-edit'),
            {
                'type': 'privatelimitedcompany',
                'annual_turnover': '<85k',
                'number_of_employees': '1-9',
                'sector_primary': 'Aerospace',
            },
            reverse('contact:export-support-step-7'),
            {
                'type': 'Choose a type of UK limited company',
                'annual_turnover': 'Please enter a turnover amount',
                'number_of_employees': 'Choose number of employees',
                'sector_primary': 'Choose a sector',
            },
        ),
        (
            reverse('contact:export-support-step-2b-edit'),
            {
                'type': 'university',
                'annual_turnover': '<85k',
                'number_of_employees': '1-9',
                'sector_primary': 'Aerospace',
            },
            reverse('contact:export-support-step-7'),
            {
                'type': 'Choose a type of organisation',
                'annual_turnover': 'Please enter a turnover amount',
                'number_of_employees': 'Choose number of employees',
                'sector_primary': 'Choose a sector',
            },
        ),
        (
            reverse('contact:export-support-step-2c-edit'),
            {
                'type': 'soletrader',
                'annual_turnover': '<85k',
                'sector_primary': 'Aerospace',
            },
            reverse('contact:export-support-step-7'),
            {
                'type': 'Choose a type of exporter',
                'annual_turnover': 'Please enter a turnover amount',
                'sector_primary': 'Choose a sector',
            },
        ),
        (
            reverse('contact:export-support-step-3-edit'),
            {
                'first_name': 'Test',  # /PS-IGNORE
                'last_name': 'Name',  # /PS-IGNORE
                'job_title': 'Test job title',
                'uk_telephone_number': '07171771717',
                'email': 'name@example.com',  # /PS-IGNORE
            },
            reverse('contact:export-support-step-7'),
            {
                'first_name': 'Enter your first name',  # /PS-IGNORE
                'last_name': 'Enter your last name',  # /PS-IGNORE
                'job_title': 'Enter your job title',  # /PS-IGNORE
                'uk_telephone_number': 'Enter your telephone number',
                'email': 'Enter an email address in the correct format, like name@example.com',  # /PS-IGNORE
            },
        ),
        (
            reverse('contact:export-support-step-4-edit'),
            {
                'product_or_service_1': 'Test product 1',
            },
            reverse('contact:export-support-step-7'),
            {
                'product_or_service_1': 'Enter a product or service',
            },
        ),
        (
            reverse('contact:export-support-step-5-edit'),
            {
                'markets': ['AU'],
            },
            reverse('contact:export-support-step-7'),
            {
                'markets': 'Enter a market',
            },
        ),
        (
            reverse('contact:export-support-step-6-edit'),
            {
                'about_your_experience': 'neverexported',
            },
            reverse('contact:export-support-step-7'),
            {
                'about_your_experience': 'Choose your export experience',
            },
        ),
    ),
)
@pytest.mark.django_db
@mock.patch('directory_forms_api_client.actions.ZendeskAction')
def test_domestic_export_support_edit_form_pages(
    mock_action_class,
    page_url,
    form_data,
    redirect_url,
    error_messages,
    client,
):
    #   Redirect fails when any of the fields in the form are missing
    invalid_form_data = form_data.copy()
    for key in form_data:
        invalid_form_data.pop(key)
        response = client.post(page_url, invalid_form_data)
        assert response.status_code == 200
        assert error_messages[key] in str(response.rendered_content)
        invalid_form_data = form_data.copy()

    #   Redirect succeeds with valid data
    response = client.post(page_url, form_data)
    assert response.status_code == 302
    assert response.url == redirect_url


@mock.patch.object(actions, 'SaveOnlyInDatabaseAction')
@pytest.mark.django_db
def test_feedback_form_success(
    mock_action_class,
    client,
    user,
):
    client.force_login(user)

    response = client.post(
        reverse('contact:export-support-step-9'),
        {
            'form_issues': ['I_did_not_find_what_I_was_looking_for'],
            'type_of_support': ['Market_selection'],
            'explored_great': 'yes',
            'how_can_we_improve': '',
        },
    )

    assert response.status_code == 302
    assert response.url == reverse('contact:export-support-step-10')

    assert mock_action_class().save.call_count == 1

    assert mock_action_class().save.call_args_list[0] == mock.call(
        {
            'form_issues': ['I_did_not_find_what_I_was_looking_for'],
            'type_of_support': ['Market_selection'],
            'explored_great': 'yes',
            'how_can_we_improve': '',
        }
    )


@mock.patch.object(actions, 'SaveOnlyInDatabaseAction')
@pytest.mark.django_db
def test_inline_feedback_js(
    mock_action_class,
    client,
    user,
):
    client.force_login(user)

    data = {'page_useful': 'True', 'current_url': '/example-url', 'page_title': 'Example Page'}

    mock_response = Response()
    mock_response.status_code = 201
    mock_action_class().save.return_value = mock_response

    response = client.post(
        f"{reverse('contact:contact-inline-feedback')}?js_enabled=True",
        data,
    )

    assert response.status_code == 201

    assert mock_action_class().save.call_count == 1

    query_dict_data = QueryDict('', mutable=True)
    query_dict_data.update(data)
    mock_action_class().save.assert_called_with(query_dict_data)


@pytest.mark.parametrize(
    'query_param, query_param_value',
    (('page_useful', 'True'), ('page_useful', 'False'), ('detailed_feedback_submitted', 'True')),
)
@mock.patch.object(actions, 'SaveOnlyInDatabaseAction')
@pytest.mark.django_db
def test_inline_feedback_non_js(
    mock_action_class,
    query_param,
    query_param_value,
    client,
):
    if query_param == 'page_useful':
        data = {'page_useful': query_param_value, 'current_url': '/example-url', 'page_title': 'Example Page'}
    elif query_param == 'detailed_feedback_submitted':
        data = {
            'easily_understood': 'True',
            'found_information_needed': 'True',
            'current_url': '/example-url',
            'page_title': 'Example Page',
        }

    mock_response = Response()
    mock_response.status_code = 201
    mock_action_class().save.return_value = mock_response

    qs = f'{query_param}={query_param_value}'
    response = client.post(
        f"{reverse('contact:contact-inline-feedback')}?{qs}",
        data,
    )

    assert response.status_code == 303

    assert f'?{qs}/#inline-feedback' in response.url

    assert mock_action_class().save.call_count == 1

    query_dict_data = QueryDict('', mutable=True)
    query_dict_data.update(data)
    mock_action_class().save.assert_called_with(query_dict_data)
