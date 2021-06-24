from unittest import mock

import django.forms
import pytest
import requests_mock
from django.conf import settings
from django.urls import reverse

from contact import constants, forms, helpers, views
from core import snippet_slugs
from directory_api_client.exporting import url_lookup_by_postcode

pytestmark = [pytest.mark.django_db, pytest.mark.contact]


def build_wizard_url(step):
    return reverse('contact:contact-us-routing-form', kwargs={'step': step})


@pytest.fixture()
def all_office_details():
    return [
        {
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
        },
        {
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
        },
    ]


class FakeChoiceForm(django.forms.Form):
    choice = django.forms.CharField()


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
        # TO BE PORTED IN SUBSEQUENT WORK
        # (
        #     reverse('contact:contact-us-exporting-to-the-trade-with-uk-app'),
        #     reverse('contact:contact-us-international-success'),
        #     views.ExportingToUKFormView,
        #     settings.CONTACT_INTERNATIONAL_ZENDESK_SUBJECT,
        #     None,
        # ),
        # (
        #     reverse('contact:contact-us-exporting-to-the-uk-import-controls'),
        #     reverse('contact:contact-us-international-success'),
        #     views.ExportingToUKFormView,
        #     settings.CONTACT_INTERNATIONAL_ZENDESK_SUBJECT,
        #     settings.EU_EXIT_ZENDESK_SUBDOMAIN,
        # ),
        # (
        #     reverse('contact:contact-us-exporting-to-the-uk-other'),
        #     reverse('contact:contact-us-international-success'),
        #     views.ExportingToUKFormView,
        #     settings.CONTACT_INTERNATIONAL_ZENDESK_SUBJECT,
        #     settings.EU_EXIT_ZENDESK_SUBDOMAIN,
        # ),
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
        # TO BE PORTED IN SUBSEQUENT WORK
        # (
        #     reverse('contact:contact-us-international'),
        #     reverse('contact:contact-us-international-success'),
        #     views.InternationalFormView,
        #     settings.CONTACT_INTERNATIONAL_AGENT_NOTIFY_TEMPLATE_ID,
        #     settings.CONTACT_INTERNATIONAL_USER_NOTIFY_TEMPLATE_ID,
        #     settings.CONTACT_INTERNATIONAL_AGENT_EMAIL_ADDRESS,
        # ),
        (
            reverse('contact:office-finder-contact', kwargs={'postcode': 'FOO'}),
            reverse('contact:contact-us-office-success', kwargs={'postcode': 'FOO'}),
            views.OfficeContactFormView,
            settings.CONTACT_OFFICE_AGENT_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_OFFICE_USER_NOTIFY_TEMPLATE_ID,
            settings.CONTACT_DIT_AGENT_EMAIL_ADDRESS,
        ),
        # (
        #     reverse('contact:contact-us-exporting-to-the-uk-beis'),
        #     reverse('contact:contact-us-exporting-to-the-uk-beis-success'),
        #     views.ExportingToUKBEISFormView,
        #     settings.CONTACT_BEIS_AGENT_NOTIFY_TEMPLATE_ID,
        #     settings.CONTACT_BEIS_USER_NOTIFY_TEMPLATE_ID,
        #     settings.CONTACT_BEIS_AGENT_EMAIL_ADDRESS,
        # ),
        # (
        #     reverse('contact:contact-us-exporting-to-the-uk-defra'),
        #     reverse('contact:contact-us-exporting-to-the-uk-defra-success'),
        #     views.ExportingToUKDERAFormView,
        #     settings.CONTACT_DEFRA_AGENT_NOTIFY_TEMPLATE_ID,
        #     settings.CONTACT_DEFRA_USER_NOTIFY_TEMPLATE_ID,
        #     settings.CONTACT_DEFRA_AGENT_EMAIL_ADDRESS,
        # )
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
def test_contact_us_short_form_not_prepopulated_if_logged_out(client, url, user):
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['form'].initial == {}


success_view_params = (
    reverse('contact:contact-us-domestic-success'),
    reverse('contact:contact-us-events-success'),
    reverse('contact:contact-us-dso-success'),
    reverse('contact:contact-us-feedback-success'),
    # TO BE PORTED IN SUBSEQUENT WORK
    # reverse('contact:contact-us-export-advice-success'),
    # reverse('contact:contact-us-international-success'),
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
        # TODO: replace URL name with contact:contact-us-routing-form with
        # kwargs={'step': 'location'} once that has been ported
        reverse('contact:contact-us-domestic'),
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
        # (
        #     constants.DOMESTIC,
        #     constants.EXPORT_ADVICE,
        #     reverse('contact:contact-us-export-advice', kwargs={'step': 'comment'}),
        # ),
        # (
        #     constants.DOMESTIC,
        #     constants.FINANCE,
        #     reverse(
        #         'uk-export-finance-lead-generation-form',
        #         kwargs={'step': 'contact'},
        #     ),
        # ),
        # (
        #     constants.DOMESTIC,
        #     constants.EUEXIT,
        #     reverse('domestic:brexit-contact-form'),
        # ),
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
        # # Export opportunities guidance routing
        # (
        #     constants.EXPORT_OPPORTUNITIES,
        #     constants.NO_RESPONSE,
        #     views.build_export_opportunites_guidance_url(snippet_slugs.HELP_EXOPPS_NO_RESPONSE),
        # ),
        # (
        #     constants.EXPORT_OPPORTUNITIES,
        #     constants.ALERTS,
        #     views.build_export_opportunites_guidance_url(snippet_slugs.HELP_EXOPP_ALERTS_IRRELEVANT),
        # ),
        # (
        #     constants.EXPORT_OPPORTUNITIES,
        #     constants.OTHER,
        #     reverse('contact:contact-us-domestic'),
        # ),
        # # international routing
        # (
        #     constants.INTERNATIONAL,
        #     constants.INVESTING,
        #     settings.INVEST_CONTACT_URL,
        # ),
        # (
        #     constants.INTERNATIONAL,
        #     constants.EXPORTING_TO_UK,
        #     views.build_exporting_guidance_url(snippet_slugs.HELP_EXPORTING_TO_UK),
        # ),
        # (
        #     constants.INTERNATIONAL,
        #     constants.BUYING,
        #     settings.FIND_A_SUPPLIER_CONTACT_URL,
        # ),
        # (
        #     constants.INTERNATIONAL,
        #     constants.OTHER,
        #     reverse('contact:contact-us-international'),
        # ),
        # # exporting to the UK routing
        # (
        #     constants.EXPORTING_TO_UK,
        #     constants.HMRC,
        #     settings.CONTACT_EXPORTING_TO_UK_HMRC_URL,
        # ),
        # (constants.EXPORTING_TO_UK, constants.DEFRA, reverse('contact:contact-us-exporting-to-the-uk-defra')),
        # (constants.EXPORTING_TO_UK, constants.BEIS, reverse('contact:contact-us-exporting-to-the-uk-beis')),
        # (constants.EXPORTING_TO_UK, constants.IMPORT_CONTROLS, reverse('contact:contact-us-international')),
        # (constants.EXPORTING_TO_UK, constants.TRADE_WITH_UK_APP, reverse('contact:contact-us-international')),
        # (
        #     constants.EXPORTING_TO_UK,
        #     constants.OTHER,
        #     reverse('contact:contact-us-international'),
        # ),
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
        (constants.INTERNATIONAL, constants.LOCATION),
        (constants.GREAT_SERVICES, constants.DOMESTIC),
        (constants.GREAT_ACCOUNT, constants.GREAT_SERVICES),
        (constants.EXPORT_OPPORTUNITIES, constants.GREAT_SERVICES),
        (constants.EXPORTING_TO_UK, constants.INTERNATIONAL),
    ),
)
def test_get_previous_step(current_step, expected_step):
    view = views.RoutingFormView()
    view.steps = mock.Mock(current=current_step)
    view.storage = mock.Mock()
    view.url_name = 'contact:contact-us-routing-form'

    assert view.get_prev_step() == expected_step


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
    view.url_name = 'contact-us-routing-form'

    assert form.is_valid()


def test_office_finder_valid(all_office_details, client):
    with requests_mock.mock() as mock:
        mock.get(url_lookup_by_postcode.format(postcode='LE191RJ'), json=all_office_details)
        response = client.get(reverse('contact:office-finder'), {'postcode': 'LE19 1RJ'})

    assert response.status_code == 200

    assert response.context_data['office_details'] == {
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
        # (
        #     reverse('contact:contact-us-export-advice-success'),
        #     snippet_slugs.HELP_FORM_SUCCESS_EXPORT_ADVICE,
        # ),
        (
            reverse('contact:contact-us-feedback-success'),
            snippet_slugs.HELP_FORM_SUCCESS_FEEDBACK,
        ),
        (
            reverse('contact:contact-us-domestic-success'),
            snippet_slugs.HELP_FORM_SUCCESS,
        ),
        # (
        #     reverse('contact:contact-us-international-success'),
        #     snippet_slugs.HELP_FORM_SUCCESS_INTERNATIONAL,
        # ),
        (
            reverse('contact:contact-us-office-success', kwargs={'postcode': 'FOOBAR'}),
            snippet_slugs.HELP_FORM_SUCCESS,
        ),
        # (
        #     reverse('contact:contact-us-exporting-to-the-uk-beis-success'),
        #     snippet_slugs.HELP_FORM_SUCCESS_BEIS,
        # ),
        # (
        #     reverse('contact:contact-us-exporting-to-the-uk-defra-success'),
        #     snippet_slugs.HELP_FORM_SUCCESS_DEFRA,
        # ),
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
