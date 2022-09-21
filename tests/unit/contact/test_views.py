from unittest import mock

import django.forms
import pytest
import requests_mock
from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse

from contact import constants, forms, helpers, views
from core import snippet_slugs
from core.constants import CONSENT_EMAIL
from core.tests.helpers import create_response
from directory_api_client.exporting import url_lookup_by_postcode

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
        'first_name': 'Test',
        'last_name': 'Name',
        'email': 'test@test.com',
        'phone_number': '+447501234567',
        'job_title': 'developer',
        'company_name': 'Limited',
        'company_postcode': 'sw1 1bb',
        'employees_number': '1-9',
        'annual_turnover': '',
        'currently_export': 'no',
        'comment': 'some comment',
        'terms_agreed': True,
        'g-recaptcha-response': captcha_stub,
    }


@pytest.fixture()
def all_office_details():
    return [
        {
            'is_match': True,
            'region_id': 'east_midlands',
            'name': 'DIT East Midlands',
            'address_street': 'The International Trade Centre, 5 Merus Court, Meridian Business Park',
            'address_city': 'Leicester',
            'address_postcode': 'LE19 1RJ',
            'email': 'test+east_midlands@examoke.com',
            'phone': '0345 052 4001',
            'phone_other': '',
            'phone_other_comment': '',
            'website': None,
        },
        {
            'is_match': False,
            'region_id': 'west_midlands',
            'name': 'DIT West Midlands',
            'address_street': 'The International Trade Centre, 10 New Street, Midlands Business Park',
            'address_city': 'Birmingham',
            'address_postcode': 'B20 1RJ',
            'email': 'test+west_midlands@examoke.com',
            'phone': '0208 555 4001',
            'phone_other': '',
            'phone_other_comment': '',
            'website': None,
        },
    ]


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
        (
            reverse('contact:contact-us-international'),
            reverse('contact:contact-us-international-success'),
            views.InternationalFormView,
            settings.CONTACT_INTERNATIONAL_AGENT_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_INTERNATIONAL_USER_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_INTERNATIONAL_AGENT_EMAIL_ADDRESS,
        ),
        (
            reverse('contact:office-finder-contact', kwargs={'postcode': 'FOO'}),
            reverse('contact:contact-us-office-success', kwargs={'postcode': 'FOO'}),
            views.OfficeContactFormView,
            settings.CONTACT_OFFICE_AGENT_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_OFFICE_USER_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_DIT_AGENT_EMAIL_ADDRESS,
        ),
    ),
)
@mock.patch.object(views.FormSessionMixin, 'form_session_class')
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
        response = client.post(url, {'email': 'test@example.com'})

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
                'email_address': 'test@example.com',
                'country_code': None,
                'ip_address': None,
            },
        ),
        mock.call(
            template_id=user_template,
            email_address='test@example.com',
            form_url=url,
            form_session=mock_form_session(),
        ),
    ]


contact_urls_for_prefill_tests = (
    reverse('contact:contact-us-domestic'),
    reverse('contact:contact-us-enquiries'),
    reverse('contact:contact-us-dso-form'),
    reverse('contact:contact-us-events-form'),
    reverse('contact:office-finder-contact', kwargs={'postcode': 'FOOBAR'}),
)


@pytest.mark.parametrize('url', contact_urls_for_prefill_tests)
def test_contact_us_short_form_prepopulated_when_logged_in(
    client,
    url,
    user,
    mock_get_company_profile,
):
    client.force_login(user)  #  ensure the user is logged in

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
    reverse('contact:contact-us-international-success'),
)


@pytest.mark.parametrize('url', success_view_params)
@mock.patch.object(views.FormSessionMixin.form_session_class, 'clear')
@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
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


@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
@mock.patch.object(views.FormSessionMixin.form_session_class, 'clear')
def test_always_landing_for_soo_ingress_url_on_success(
    mock_clear,
    mock_get_snippet_instance,
    client,
    rf,
):
    mock_clear.return_value = None
    mocked_soo_landing = 'http://testserver.com/test-path/'
    client.get(
        reverse('contact:contact-us-soo', kwargs={'step': 'organisation'}),
        HTTP_REFERER=mocked_soo_landing + 'markets/details/ebay/',
        HTTP_HOST='testserver.com',
    )
    # when the success page is viewed
    with mock.patch('directory_constants.urls.domestic.SELLING_OVERSEAS', mocked_soo_landing):
        response = client.get(reverse('contact:contact-us-selling-online-overseas-success'), HTTP_HOST='testserver.com')
    # for contact ingress urls user flow continues to landing page
    assert response.context_data['next_url'] == mocked_soo_landing
    assert response.context_data['next_url_text'] == 'Go back to Selling Online Overseas'
    assert response.status_code == 200
    # and the ingress url is cleared
    assert mock_clear.call_count == 1
    assert mock_get_snippet_instance.call_count == 1


@pytest.mark.parametrize('url', success_view_params)
@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
@mock.patch.object(views.FormSessionMixin.form_session_class, 'clear')
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
                'email_address': 'test@test.com',
                'country_code': None,
                'ip_address': None,
            },
            template_id=settings.CONTACT_ECOMMERCE_EXPORT_SUPPORT_AGENT_NOTIFY_TEMPLATE_ID,
        ),
        mock.call(
            email_address='test@test.com',
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
        # domestic step routing
        (
            constants.DOMESTIC,
            constants.TRADE_OFFICE,
            reverse('contact:office-finder'),
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
        # (constants.INTERNATIONAL, constants.LOCATION),  /international/contact/ is run by great-international-ui
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


def test_office_finder_valid(all_office_details, client):
    with requests_mock.mock() as mock:
        mock.get(url_lookup_by_postcode.format(postcode='LE191RJ'), json=all_office_details)
        response = client.get(reverse('contact:office-finder'), {'postcode': 'LE19 1RJ'})

    assert response.status_code == 200

    assert response.context_data['office_details'][0] == {
        'address': (
            'The International Trade Centre\n' '5 Merus Court\n' 'Meridian Business Park\n' 'Leicester\n' 'LE19 1RJ'
        ),
        'is_match': True,
        'region_id': 'east_midlands',
        'name': 'DIT East Midlands',
        'address_street': ('The International Trade Centre, ' '5 Merus Court, ' 'Meridian Business Park'),
        'address_city': 'Leicester',
        'address_postcode': 'LE19 1RJ',
        'email': 'test+east_midlands@examoke.com',
        'phone': '0345 052 4001',
        'phone_other': '',
        'phone_other_comment': '',
        'website': None,
    }

    assert response.context_data['other_offices'] == [
        {
            'address': (
                'The International Trade Centre\n' '10 New Street\n' 'Midlands Business Park\n' 'Birmingham\n' 'B20 1RJ'
            ),
            'is_match': False,
            'region_id': 'west_midlands',
            'name': 'DIT West Midlands',
            'address_street': ('The International Trade Centre, ' '10 New Street, ' 'Midlands Business Park'),
            'address_city': 'Birmingham',
            'address_postcode': 'B20 1RJ',
            'email': 'test+west_midlands@examoke.com',
            'phone': '0208 555 4001',
            'phone_other': '',
            'phone_other_comment': '',
            'website': None,
        }
    ]


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
        (
            reverse('contact:contact-us-international-success'),
            snippet_slugs.HELP_FORM_SUCCESS_INTERNATIONAL,
        ),
        (
            reverse('contact:contact-us-office-success', kwargs={'postcode': 'FOOBAR'}),
            snippet_slugs.HELP_FORM_SUCCESS,
        ),
    ),
)
@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
def test_success_view_cms_snippet_data(mock_get_snippet_instance, url, slug, client):

    response = client.get(url)

    assert response.status_code == 200
    mock_get_snippet_instance.assert_called_once()


@mock.patch('core.mixins.GetSnippetContentMixin.get_snippet_instance')
def test_contact_us_office_success_next_url(mock_get_snippet_instance, client):

    url = reverse(
        'contact:contact-us-office-success',
        kwargs={'postcode': 'FOOBAR'},
    )

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['next_url'] == '/'

    mock_get_snippet_instance.assert_called_once()


def test_contact_us_feedback_prepopulate(
    client,
    user,
    mock_get_company_profile,
):
    client.force_login(user)  #  ensure the user is logged in

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
    mock_retrieve_regional_office_email.return_value = 'regional@example.com'

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
            'personal-first_name': 'test',
            'personal-last_name': 'test',
            'personal-position': 'test',
            'personal-email': 'test@example.com',
            'personal-phone': 'test',
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
        email_address='test@example.com',
        form_url='/contact/export-advice/comment/',
        form_session=mock_form_session(),
        email_reply_to_id=settings.CONTACT_EXPORTING_USER_REPLY_TO_EMAIL_ID,
    )
    assert mock_notify_action().save.call_count == 1
    assert mock_notify_action().save.call_args == mock.call(
        {
            'comment': 'some comment',
            'first_name': 'test',
            'last_name': 'test',
            'position': 'test',
            'email': 'test@example.com',
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
            'region_office_email': 'regional@example.com',
            'contact_consent': [CONSENT_EMAIL],
        }
    )

    assert mock_email_action.call_count == 1
    assert mock_email_action.call_args == mock.call(
        recipients=['regional@example.com'],
        subject=settings.CONTACT_EXPORTING_AGENT_SUBJECT,
        reply_to=[settings.DEFAULT_FROM_EMAIL],
        form_url='/contact/export-advice/comment/',
        form_session=mock_form_session(),
        sender={'email_address': 'test@example.com', 'country_code': None, 'ip_address': None},
    )
    assert mock_email_action().save.call_count == 1
    assert mock_email_action().save.call_args == mock.call({'text_body': mock.ANY, 'html_body': mock.ANY})

    assert mock_retrieve_regional_office_email.call_count == 1
    assert mock_retrieve_regional_office_email.call_args == mock.call('1234')


@mock.patch('captcha.fields.ReCaptchaField.clean')
@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@mock.patch('directory_forms_api_client.actions.EmailAction')
@mock.patch('contact.helpers.retrieve_regional_office_email')
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

    mock_retrieve_regional_office_email.return_value = 'regional@example.com'

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


def test_contact_us_international_prepopualate(client, user, mock_get_company_profile):
    url = reverse('contact:contact-us-international')

    mock_get_company_profile.return_value = {
        # Full spec of CompanySerializer is in
        # https://github.com/uktrade/directory-api/blob/master/company/serializers.py
        'name': 'Example corp',
        'locality': 'Paris',
        'country': 'FRANCE',
    }

    client.force_login(user)

    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['form'].initial == {
        'email': user.email,
        'organisation_name': 'Example corp',
        'country_name': 'FRANCE',
        'city': 'Paris',
        'family_name': 'Cross',
        'given_name': 'Jim',
    }


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


def test_selling_online_overseas_contact_form_organisation_url_redirect(
    client,
    user,
):
    # Needs to be authenticated to avoid a redirect to the SSO service
    client.force_login(user)

    response = client.get(
        reverse(
            'contact:contact-us-soo',
            kwargs={
                'step': 'organisation',
            },
        )
    )
    assert response.status_code == 302
    assert response.url == reverse(
        'contact:contact-us-soo',
        kwargs={
            'step': 'contact-details',
        },
    )


@override_settings(
    CACHES={
        # Because we can't use the DummyCache here
        'default': locmem_cache_spec,
        'api_fallback': locmem_cache_spec,
    }
)
@pytest.mark.parametrize('flow', ('CH Company', 'Non-CH Company', 'Individual'))
@mock.patch('directory_forms_api_client.actions.ZendeskAction')
@mock.patch.object(views.FormSessionMixin, 'form_session_class')
@mock.patch('sso.helpers.sso_api_client.user.update_user_profile')
def test_selling_online_overseas_contact_form_submission(  # noqa: C901
    mock_sso_call,
    mock_form_session,
    mock_zendesk_action,
    flow,
    user,
    client,
    mock_get_company_profile,
):

    client.force_login(user)

    def post(step, args):
        return client.post(
            reverse(
                url_name,
                kwargs={'step': step},
            ),
            {view_name + '-current_step': step, **args},
        )

    # Set Directory-API company lookup
    if flow == 'CH Company':
        mock_get_company_profile.return_value = {
            'company_type': 'COMPANIES_HOUSE',
            'number': 1234567,
            'name': 'Example corp',
            'postal_code': 'Foo Bar',
            'sectors': ['AEROSPACE'],
            'employees': '1-10',
            'mobile_number': '07171771717',
            'postal_full_name': 'Foo Example',
            'address_line_1': '123 Street',
            'address_line_2': 'Near Fake Town',
            'country': 'FRANCE',
            'locality': 'Paris',
            'summary': 'Makes widgets',
            'website': 'http://www.example.com',
        }
    if flow == 'Non-CH Company':
        mock_get_company_profile.return_value = {
            # Full spec of CompanySerializer is in
            # https://github.com/uktrade/directory-api/blob/master/company/serializers.py
            'company_type': 'SOLE_TRADER',
            'name': 'Example corp',
            'postal_code': 'Foo Bar',
            'sectors': ['Aerospace'],
            'employees': '1-10',
            'mobile_number': '07171771717',
            'postal_full_name': 'Foo Example',
            'address_line_1': '123 Street',
            'address_line_2': 'Near Fake Town',
            'country': 'FRANCE',
            'locality': 'Paris',
            'summary': 'Makes widgets',
            'website': 'http://www.example.com',
        }
    if flow == 'Individual':
        mock_get_company_profile.return_value = create_response(status_code=404)

    # Shortcut for company type
    try:
        company_type = getattr(user.company, 'company_type', None)
    except AttributeError:
        company_type = None

    url_name = 'contact:contact-us-soo'
    view_name = 'selling_online_overseas_form_view'

    # Get the 1st step
    client.get(
        reverse(url_name, kwargs={'step': 'contact-details'}),
        {'market': 'ebay'},
    )

    # Submit the 1st step

    # Note that the user and company fixtures will auto-fill in the details
    # where the form requires it. You can only add optional data
    # to the POST requests.
    response = post(
        'contact-details',
        {
            'contact-details-phone': '55512345',
            'contact-details-email_pref': True,
        },
    )
    assert response.status_code == 302

    if company_type == 'COMPANIES_HOUSE':
        # Name, number and address auto-filled
        response = post(
            'applicant',
            {
                'applicant-website_address': 'http://fooexample.com',
                'applicant-turnover': 'Under 100k',
            },
        )
    elif company_type == 'SOLE_TRADER':
        # Name, address auto-filled
        response = post(
            'applicant',
            {
                'applicant-website_address': 'http://fooexample.com',
                'applicant-turnover': 'Under 100k',
            },
        )
    elif company_type is None:
        response = post(
            'applicant',
            {
                'applicant-company_name': 'Super corp',
                'applicant-company_number': 662222,
                'applicant-company_address': '99 Street',
                'applicant-company_postcode': 'N1 123',
                'applicant-website_address': 'http://barexample.com',
                'applicant-turnover': 'Under 100k',
            },
        )
    assert response.status_code == 302

    response = post(
        'applicant-details',
        {
            'applicant-details-sku_count': 12,
            'applicant-details-trademarked': True,
        },
    )
    assert response.status_code == 302

    response = post(
        'your-experience',
        {
            'your-experience-experience': 'Not yet',
            'your-experience-description': 'Makes widgets',
        },
    )

    assert response.status_code == 302
    response = client.get(response.url)
    assert response.status_code == 302

    assert response.url == reverse('contact:contact-us-selling-online-overseas-success')

    # check first_name, last_name  sent to directory-sso for profile update
    assert mock_sso_call.call_count == 1
    assert mock_sso_call.call_args == mock.call('123', {'first_name': 'Jim', 'last_name': 'Cross'})

    # Check data sent to Zendesk
    assert mock_zendesk_action.call_count == 1
    assert mock_zendesk_action.call_args == mock.call(
        subject=settings.CONTACT_SOO_ZENDESK_SUBJECT,
        full_name=user.get_full_name(),
        sender={'email_address': user.email, 'country_code': None, 'ip_address': None},
        email_address=user.email,
        service_name='soo',
        form_url=reverse('contact:contact-us-soo', kwargs={'step': 'contact-details'}),
        form_session=mock_form_session(),
    )
    assert mock_zendesk_action().save.call_count == 1

    expected_data = {
        'market': 'ebay',
        'contact_first_name': 'Jim',
        'contact_last_name': 'Cross',
        'contact_email': 'jim@example.com',
        'phone': '55512345',
        'email_pref': True,
        'sku_count': 12,
        'trademarked': True,
        'experience': 'Not yet',
        'description': 'Makes widgets',
    }
    if company_type == 'COMPANIES_HOUSE':
        expected_data.update(
            {
                'company_name': 'Example corp',
                'company_number': '1234567',
                'company_address': '123 Street, Near Fake Town',
                'website_address': 'http://fooexample.com',
                'turnover': 'Under 100k',
            }
        )
    elif company_type == 'SOLE_TRADER':
        expected_data.update(
            {
                'company_name': 'Example corp',
                'company_address': '123 Street, Near Fake Town',
                'website_address': 'http://fooexample.com',
                'turnover': 'Under 100k',
            }
        )
    elif company_type is None:
        expected_data.update(
            {
                'company_name': 'Super corp',
                'company_number': '662222',
                'company_address': '99 Street',
                'company_postcode': 'N1 123',
                'website_address': 'http://barexample.com',
                'turnover': 'Under 100k',
            }
        )

    cache_key = f'{view_name}_{user.id}'
    assert mock_zendesk_action().save.call_args == mock.call(expected_data)
    assert cache.get(cache_key) == expected_data
    # next request for the form will have initial values
    response = client.get(
        reverse(url_name, kwargs={'step': 'contact-details'}),
        {'market': 'ebay'},
    )

    # Initial data contains phone number if company profile present
    if company_type in ['COMPANIES_HOUSE', 'SOLE_TRADER']:
        assert response.context_data['form'].initial == {
            'contact_first_name': 'Jim',
            'contact_last_name': 'Cross',
            'contact_email': 'jim@example.com',
            'phone': '55512345',
        }
    else:
        assert response.context_data['form'].initial == {
            'contact_first_name': 'Jim',
            'contact_last_name': 'Cross',
            'contact_email': 'jim@example.com',
            'phone': '55512345',
        }


@override_settings(
    CACHES={
        # Because we can't use the DummyCache here
        'default': locmem_cache_spec,
        'api_fallback': locmem_cache_spec,
    }
)
def test_selling_online_overseas_contact_form_market_name(client, user):

    client.force_login(user)

    url_name = 'contact:contact-us-soo'

    response = client.get(
        reverse(url_name, kwargs={'step': 'contact-details'}),
        {'market': 'ebay'},
    )
    assert response.status_code == 200
    assert response.context['market_name'] == 'ebay'

    response = client.get(
        reverse(url_name, kwargs={'step': 'applicant'}),
    )
    assert response.status_code == 200
    assert response.context['market_name'] == 'ebay'

    response = client.get(
        reverse(url_name, kwargs={'step': 'applicant-details'}),
    )
    assert response.status_code == 200
    assert response.context['market_name'] == 'ebay'

    response = client.get(
        reverse(url_name, kwargs={'step': 'your-experience'}),
    )
    assert response.status_code == 200
    assert response.context['market_name'] == 'ebay'


@pytest.mark.parametrize('flow', ('CH Company', 'Non-CH Company', 'Individual'))
def test_selling_online_overseas_contact_form_initial_data(  # noqa: C901
    flow,
    mock_get_company_profile,
    user,
    client,
):

    client.force_login(user)

    # Set Directory-API company lookup
    if flow == 'CH Company':
        mock_get_company_profile.return_value = {
            'company_type': 'COMPANIES_HOUSE',
            'number': 1234567,
            'name': 'Example corp',
            'postal_code': 'Foo Bar',
            'sectors': ['AEROSPACE'],
            'employees': '1-10',
            'mobile_number': '07171771717',
            'postal_full_name': 'Foo Example',
            'address_line_1': '123 Street',
            'address_line_2': 'Near Fake Town',
            'country': 'FRANCE',
            'locality': 'Paris',
            'summary': 'Makes widgets',
            'website': 'http://www.example.com',
        }

    if flow == 'Non-CH Company':
        mock_get_company_profile.return_value = {
            # Full spec of CompanySerializer is in
            # https://github.com/uktrade/directory-api/blob/master/company/serializers.py
            'company_type': 'SOLE_TRADER',
            'name': 'Example corp',
            'postal_code': 'Foo Bar',
            'sectors': ['Aerospace'],
            'employees': '1-10',
            'mobile_number': '07171771717',
            'postal_full_name': 'Foo Example',
            'address_line_1': '123 Street',
            'address_line_2': 'Near Fake Town',
            'country': 'FRANCE',
            'locality': 'Paris',
            'summary': 'Makes widgets',
            'website': 'http://www.example.com',
        }

    if flow == 'Individual':
        mock_get_company_profile.return_value = create_response(status_code=404)

    response = client.get(
        reverse('contact:contact-us-soo', kwargs={'step': 'contact-details'}),
    )
    if flow in ['CH Company', 'Non-CH Company']:
        assert response.context_data['form'].initial == {
            'contact_first_name': 'Jim',
            'contact_last_name': 'Cross',
            'contact_email': 'jim@example.com',
            'phone': '55512345',
        }
    else:
        assert response.context_data['form'].initial == {
            'contact_first_name': 'Jim',
            'contact_last_name': 'Cross',
            'contact_email': 'jim@example.com',
            'phone': '55512345',
        }

    response = client.get(
        reverse('contact:contact-us-soo', kwargs={'step': 'applicant'}),
    )
    if flow == 'CH Company':
        assert response.context_data['form'].initial == {
            'company_name': 'Example corp',
            'company_address': '123 Street, Near Fake Town',
            'company_number': 1234567,
            'website_address': 'http://www.example.com',
        }
    if flow == 'Non-CH Company':
        assert response.context_data['form'].initial == {
            'company_name': 'Example corp',
            'company_address': '123 Street, Near Fake Town',
            'website_address': 'http://www.example.com',
        }
    if flow == 'Individual':
        assert response.context_data['form'].initial == {}

    response = client.get(
        reverse('contact:contact-us-soo', kwargs={'step': 'applicant-details'}),
    )
    assert response.context_data['form'].initial == {}

    response = client.get(
        reverse('contact:contact-us-soo', kwargs={'step': 'your-experience'}),
    )
    if flow in ['CH Company', 'Non-CH Company']:
        assert response.context_data['form'].initial == {'description': 'Makes widgets'}
    else:
        assert response.context_data['form'].initial == {}
