import pickle
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


contact_urls_for_prefill_tests = (
    reverse('contact:contact-us-domestic'),
    reverse('contact:contact-us-enquiries'),
    reverse('contact:contact-us-dso-form'),
    reverse('contact:contact-us-events-form'),
    reverse('contact:office-finder-contact', kwargs={'postcode': 'FOOBAR'}),
)


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


@mock.patch.object(views.FormSessionMixin, 'form_session_class')
def test_fta_form_submit_success(mock_form_session, client, settings):
    class Form(forms.SerializeDataMixin, django.forms.Form):
        email = django.forms.EmailField()
        save = mock.Mock()

    with mock.patch.object(views.FTASubscribeFormView, 'form_class', Form):
        response = client.post(reverse('contact:contact-free-trade-agreements'), {'email': 'test@example.com'})

    assert response.status_code == 302
    assert response.url == reverse('contact:contact-free-trade-agreements-success')

    assert Form.save.call_count == 1
    assert Form.save.call_args_list == [
        mock.call(
            template_id=settings.SUBSCRIBE_TO_FTA_UPDATES_NOTIFY_TEMPLATE_ID,
            email_address='test@example.com',
            form_url=reverse('contact:contact-free-trade-agreements'),
            form_session=mock_form_session(),
        ),
    ]


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url,error_messages',
    (
        (
            reverse('contact:export-support'),
            {
                'business_type': 'limitedcompany',
                'business_name': 'Test business ltd',
                'business_postcode': 'SW1A 1AA',
            },
            reverse('contact:export-support-step-2a'),
            {
                'business_type': 'Choose a business type',
                'business_name': 'Enter your business name',
                'business_postcode': 'Enter your business postcode',
            },
        ),
        (
            reverse('contact:export-support'),
            {
                'business_type': 'other',
                'business_name': 'Test business ltd',
                'business_postcode': 'SW1A 1AA',
            },
            reverse('contact:export-support-step-2b'),
            {
                'business_type': 'Choose a business type',
                'business_name': 'Enter your business name',
                'business_postcode': 'Enter your business postcode',
            },
        ),
        (
            reverse('contact:export-support'),
            {
                'business_type': 'soletrader',
                'business_name': 'Test business ltd',
                'business_postcode': 'SW1A 1AA',
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
                'first_name': 'Test',
                'last_name': 'Name',
                'job_title': 'Test job title',
                'uk_telephone_number': '07171771717',
                'email': 'name@example.com',
            },
            reverse('contact:export-support-step-4'),
            {
                'first_name': 'Enter your first name',
                'last_name': 'Enter your last name',
                'job_title': 'Enter your job title',
                'uk_telephone_number': 'Enter your telephone number',
                'email': 'Enter an email address in the correct format, like name@example.com',
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
):
    #   Redirect fails when any of the fields in the form are missing
    invalid_form_data = form_data.copy()
    for key in form_data:
        invalid_form_data.pop(key)
        response = client.post(page_url, invalid_form_data)
        assert response.status_code == 200
        assert error_messages[key] in str(response.rendered_content)
        assert '<meta name="robots" content="noindex">' in str(response.rendered_content)

        invalid_form_data = form_data.copy()

    #   Redirect succeeds with valid data
    response = client.post(page_url, form_data)
    assert response.status_code == 302
    assert response.url == redirect_url


@pytest.mark.parametrize(
    'page_url,form_data,redirect_url,error_messages',
    (
        (
            reverse('contact:export-support-step-8'),
            {
                'help_us_improve': 'easy',
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
                'business_type': 'soletrader',
                'business_name': 'Test business ltd',
                'business_postcode': 'SW1A 1AA',
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
                'first_name': 'Test',
                'last_name': 'Name',
                'job_title': 'Test job title',
                'uk_telephone_number': '07171771717',
                'email': 'name@example.com',
            },
            reverse('contact:export-support-step-7'),
            {
                'first_name': 'Enter your first name',
                'last_name': 'Enter your last name',
                'job_title': 'Enter your job title',
                'uk_telephone_number': 'Enter your telephone number',
                'email': 'Enter an email address in the correct format, like name@example.com',
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
        reverse('contact:export-support-step-8'),
        {'help_us_improve': 'easy', 'help_us_further': 'yes'},
    )

    assert response.status_code == 302
    assert response.url == reverse('contact:export-support-step-9')

    assert mock_action_class().save.call_count == 1

    assert mock_action_class().save.call_args_list[0] == mock.call(
        {'help_us_improve': 'easy', 'help_us_further': 'yes'}
    )


@mock.patch('contact.helpers.retrieve_regional_offices')
def test_regional_office_not_displayed_on_confirmation_page(
    mock_retrieve_regional_offices,
    client,
    user,
):
    mock_retrieve_regional_offices.return_value = [
        {
            'address': (
                'The International Trade Centre\n' '5 Merus Court\n' 'Meridian Business Park\n' 'Leicester\n' 'LE19 1RJ'
            ),
            'is_match': True,
            'region_id': 'east_midlands',
            'name': 'DIT East Midlands',
            'address_street': 'The International Trade Centre, ' '5 Merus Court, ' 'Meridian Business Park',
            'address_city': 'Leicester',
            'address_postcode': 'LE19 1RJ',
            'email': 'test+east_midlands@examoke.com',
            'phone': '0345 052 4001',
            'phone_other': '',
            'phone_other_comment': '',
            'website': None,
        }
    ]
    client.force_login(user)
    session = client.session
    form_data = ({'business_postcode': 'LE19 1RJ'},)
    form_data = pickle.dumps(form_data).hex()
    session['form_data'] = form_data
    session.save()

    response = client.get(reverse('contact:export-support-step-8'))

    assert '<address>' not in str(response.rendered_content)


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
