from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser
from django.contrib.sessions.backends import signed_cookies
from django.core.exceptions import ValidationError
from django.urls import resolve, reverse
from django.views.generic import TemplateView
from formtools.wizard.views import NamedUrlSessionWizardView
from freezegun import freeze_time
from requests.exceptions import HTTPError

from directory_constants import urls, user_roles
from sso import helpers as sso_helpers
from sso.models import BusinessSSOUser
from sso_profile.enrolment import constants, forms, helpers, mixins, views
from ..common.helpers import create_response, submit_step_factory

pytestmark = pytest.mark.django_db

enrolment_urls = (
    reverse('sso_profile:enrolment-business-type'),
    reverse('sso_profile:enrolment-start'),
    reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.USER_ACCOUNT}),
    reverse('sso_profile:enrolment-sole-trader', kwargs={'step': constants.USER_ACCOUNT}),
    reverse('sso_profile:enrolment-individual', kwargs={'step': constants.USER_ACCOUNT}),
)
company_types = (constants.COMPANIES_HOUSE_COMPANY, constants.NON_COMPANIES_HOUSE_COMPANY)
BUSINESS_INFO_NON_COMPANIES_HOUSE = 'business-info-non-companies-house'
BUSINESS_INFO_COMPANIES_HOUSE = 'business-info-companies-house'
ADDRESS_SEARCH_COMPANIES_HOUSE = 'address-search-companies-house'


@pytest.fixture
def user():
    return BusinessSSOUser(
        id=1,
        pk=1,
        mobile_phone_number='55512345',
        email='jim@example.com',  # /PS-IGNORE
        first_name='Jim',
        last_name='Cross',
        session_id='123',
        has_user_profile=False,
    )


@pytest.fixture
def submit_collaborator_enrolment_step(client):
    return submit_step_factory(
        client=client,
        url_name='sso_profile:enrolment-collaboration',
        view_class=views.CollaboratorEnrolmentView,
    )


@pytest.fixture
def submit_companies_house_step(client):
    return submit_step_factory(
        client=client,
        url_name='sso_profile:enrolment-companies-house',
        view_class=views.CompaniesHouseEnrolmentView,
    )


@pytest.fixture
def submit_non_companies_house_step(client):
    return submit_step_factory(
        client=client,
        url_name='sso_profile:enrolment-sole-trader',
        view_class=views.NonCompaniesHouseEnrolmentView,
    )


@pytest.fixture
def submit_individual_step(client):
    return submit_step_factory(
        client,
        url_name='sso_profile:enrolment-individual',
        view_class=views.IndividualUserEnrolmentView,
    )


@pytest.fixture
def submit_pre_verified_step(client):
    return submit_step_factory(
        client=client,
        url_name='sso_profile:enrolment-pre-verified',
        view_class=views.PreVerifiedEnrolmentView,
    )


@pytest.fixture
def submit_step_builder(
    submit_companies_house_step,
    submit_non_companies_house_step,
    submit_individual_step,
):
    def inner(choice):
        if choice == constants.COMPANIES_HOUSE_COMPANY:
            return submit_companies_house_step
        elif choice == constants.NON_COMPANIES_HOUSE_COMPANY:
            return submit_non_companies_house_step
        elif choice == constants.NOT_COMPANY:
            return submit_individual_step

    return inner


@pytest.fixture
def submit_resend_verification_house_step(client):
    return submit_step_factory(
        client=client, url_name='sso_profile:resend-verification', view_class=views.ResendVerificationCodeView
    )


@pytest.fixture
def preverified_company_data():
    return {
        'address_line_1': '23 Example lane',
        'address_line_2': 'Example land',
        'company_type': 'COMPANIES_HOUSE',
        'name': 'Example corp',
        'number': '1234567',
        'po_box': '',
        'postal_code': 'EE3 3EE',  # /PS-IGNORE
    }


@pytest.fixture(autouse=True)
def mock_retrieve_preverified_company(preverified_company_data):
    patch = mock.patch.object(
        helpers.api_client.enrolment,
        'retrieve_prepeveried_company',
        return_value=create_response(preverified_company_data),
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_collaborator_invite_accept():
    patch = mock.patch.object(helpers.api_client.company, 'collaborator_invite_accept', return_value=create_response())
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_collaborator_invite_retrieve():
    response = create_response(
        {
            'uuid': 'daca6991-21a1-4318-bc84-69349b89c26d',
            'collaborator_email': 'jim@example.com',  # /PS-IGNORE
            'company': '1',
            'requestor': '2',
            'accepted': False,
            'accepted_date': None,
            'role': user_roles.ADMIN,
        }
    )
    patch = mock.patch.object(helpers.api_client.company, 'collaborator_invite_retrieve', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_get_company_profile():
    patch = mock.patch.object(
        helpers,
        'get_companies_house_profile',
        return_value={
            'company_number': '12345678',
            'company_name': 'Example corp',
            'sic_codes': ['1234'],
            'date_of_creation': '2001-01-20',
            'registered_office_address': {'address_line_1': '555 fake street, London', 'postal_code': 'EDG 4DF'},
            'company_status': 'active',
        },
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_send_verification_code_email():
    patch = mock.patch.object(sso_helpers, 'send_verification_code_email')
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_clean():
    patch = mock.patch('captcha.fields.ReCaptchaField.clean')
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_retrieve_public_profile(client):
    patch = mock.patch.object(
        helpers.api_client.company, 'published_profile_retrieve', return_value=create_response(status_code=404)
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_validate_company_number(client):
    patch = mock.patch.object(
        helpers.api_client.company, 'validate_company_number', return_value=create_response(status_code=200)
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_collaboration_request_create(client):
    patch = mock.patch.object(
        helpers.api_client.company, 'collaboration_request_create', return_value=create_response()
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_add_collaborator(client):
    response = create_response(
        status_code=201,
        json_body={
            'sso_id': 300,
            'name': 'Abc',
            'company': 12345,
            'company_email': 'xyz@xyzcorp.com',  # /PS-IGNORE
            'mobile_number': '9876543210',
            'role': user_roles.MEMBER,
        },
    )
    patch = mock.patch.object(helpers.api_client.company, 'collaborator_create', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_get_company_admins(client):
    response = [
        {
            'company_email': 'admin@xyzcorp.com',  # /PS-IGNORE
            'company': '12345',
            'sso_id': 1,
            'name': 'Jim Abc',
            'mobile_number': '123456789',
            'role': user_roles.ADMIN,
        },
        {
            'company_email': 'admin2@xyzcorp.com',  # /PS-IGNORE
            'company': '12345',
            'sso_id': 2,
            'name': 'Pete Abc',
            'mobile_number': '123436789',
            'role': user_roles.ADMIN,
        },
    ]
    patch = mock.patch.object(views, 'get_company_admins', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_enrolment_send(client):
    patch = mock.patch.object(helpers.api_client.enrolment, 'send_form', return_value=create_response(status_code=201))
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_claim_company(client):
    patch = mock.patch.object(helpers.api_client.enrolment, 'claim_prepeveried_company', return_value=create_response())
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_create_user():
    response = create_response({'email': 'test@test.com', 'verification_code': '123456'})  # /PS-IGNORE
    patch = mock.patch.object(helpers.sso_api_client.user, 'create_user', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_user_has_company():
    patch = mock.patch.object(
        helpers.api_client.company, 'profile_retrieve', return_value=create_response(status_code=404)
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_confirm_verification_code():
    response = create_response()
    patch = mock.patch.object(helpers.sso_api_client.user, 'verify_verification_code', return_value=response)
    response.headers['set-cookie'] = (
        'debug_sso_session_cookie=foo-bar; '
        'Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; '
        'HttpOnly; '
        'Max-Age=1209600; '
        'Path=/; '
        'Secure, '
        'sso_display_logged_in=true; '
        'Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; '
        'Max-Age=1209600; '
        'Path=/'
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_regenerate_verification_code():
    response = create_response({'code': '12345', 'expiration_date': '2018-01-17T12:00:01Z'})
    patch = mock.patch.object(helpers.sso_api_client.user, 'regenerate_verification_code', return_value=response)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_notify_already_registered():
    patch = mock.patch.object(helpers, 'notify_already_registered')
    yield patch.start()
    patch.stop()


@pytest.fixture
def steps_data(captcha_stub):
    data = {
        constants.USER_ACCOUNT: {
            'email': 'jim@example.com',  # /PS-IGNORE
            'password': 'thing',
            'password_confirmed': 'thing',
            'captcha': captcha_stub,
            'terms_agreed': True,
        },
        constants.COMPANY_SEARCH: {'company_name': 'Example corp', 'company_number': '12345678'},
        constants.PERSONAL_INFO: {
            'given_name': 'Foo',
            'family_name': 'Example',
            'job_title': 'Exampler',
            'phone_number': '1232342',
            'confirmed_is_company_representative': True,
        },
        constants.VERIFICATION: {'code': '12345'},
        constants.RESEND_VERIFICATION: {'email': 'jim@example.com'},  # /PS-IGNORE
        BUSINESS_INFO_NON_COMPANIES_HOUSE: {
            'company_type': 'SOLE_TRADER',
            'company_name': 'Test company',
            'postal_code': 'EEA 3AD',
            'address': '555 fake street, London',
            'sectors': 'AEROSPACE',
        },
        BUSINESS_INFO_COMPANIES_HOUSE: {'company_name': 'Example corp', 'sectors': 'AEROSPACE'},
        ADDRESS_SEARCH_COMPANIES_HOUSE: {'company_name': 'Example corp', 'postal_code': 'EEA 3AD'},
    }
    return data


@pytest.mark.parametrize('url', enrolment_urls)
def test_200_feature_on(url, client):
    response = client.get(url)

    assert response.status_code == 200


@pytest.fixture
def session_client_company_factory(client, settings):
    def session_client(company_choice):
        session = client.session
        session[constants.SESSION_KEY_COMPANY_CHOICE] = company_choice
        session.save()
        client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key
        return client

    return session_client


@pytest.fixture
def session_intent_factory(client):
    def session_intent(intent):
        session = client.session
        session[intent] = intent
        session.save()
        return client

    return session_intent


@pytest.fixture
def session_client_referrer_factory(client, settings):
    def session_client(referrer_url):
        session = signed_cookies.SessionStore()
        session.save()
        session[constants.SESSION_KEY_REFERRER] = referrer_url
        session.save()
        client.cookies[settings.SESSION_COOKIE_NAME] = session.session_key
        return client

    return session_client


@pytest.mark.parametrize(
    'choice,expected_url',
    (
        (constants.COMPANIES_HOUSE_COMPANY, views.URL_COMPANIES_HOUSE_ENROLMENT),
        (constants.NON_COMPANIES_HOUSE_COMPANY, views.URL_NON_COMPANIES_HOUSE_ENROLMENT),
        (constants.OVERSEAS_COMPANY, views.URL_OVERSEAS_BUSINESS_ENROLMENT),
        (constants.NOT_COMPANY, views.URL_INDIVIDUAL_ENROLMENT),
    ),
)
def test_enrolment_routing(client, choice, expected_url):
    url = reverse('sso_profile:enrolment-business-type')

    response = client.post(url, {'choice': choice})

    assert response.status_code == 302
    assert response.url == expected_url


def test_enrolment_routing_individual_business_profile_intent(client, user):
    response = client.get(reverse('sso_profile:enrolment-business-type'), {'business-profile-intent': True})
    assert response.status_code == 200

    url = reverse('sso_profile:enrolment-business-type')

    response = client.post(url, {'choice': constants.NOT_COMPANY})

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:enrolment-individual-interstitial')


def test_enrolment_is_new_enrollement(client, submit_companies_house_step, steps_data, user):
    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302
    client.force_login(user)
    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH])
    assert response.status_code == 302
    response = client.get(reverse('sso_profile:enrolment-business-type'), {'new_enrollment': True})
    assert response.status_code == 200


def test_enrolment_is_not_new_enrollement_has_profile(client, submit_companies_house_step, steps_data, user):
    user.has_user_profile = True
    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302
    client.force_login(user)
    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH])
    assert response.status_code == 302
    response = client.get(reverse('sso_profile:enrolment-business-type'), {'new_enrollment': False})
    assert response.status_code == 200


def test_companies_house_enrolment(client, submit_companies_house_step, steps_data, user):
    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH])
    assert response.status_code == 302

    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )
    assert response.status_code == 302

    response = submit_companies_house_step(data=steps_data[constants.PERSONAL_INFO], step_name=constants.PERSONAL_INFO)
    assert response.status_code == 302


def test_companies_house_enrolment_already_has_profile(client, submit_companies_house_step, steps_data, user):
    user.has_user_profile = True
    user.first_name = 'Foo'
    user.last_name = 'Bar'
    client.force_login(user)

    response = submit_companies_house_step(
        data=steps_data[constants.COMPANY_SEARCH], step_name=constants.COMPANY_SEARCH
    )

    assert response.status_code == 302

    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )
    assert response.status_code == 302

    response = client.get(response.url)
    assert response.status_code == 200
    assert response.template_name == views.CompaniesHouseEnrolmentView.templates[constants.FINISHED]


@mock.patch('sso_profile.enrolment.helpers.get_is_enrolled')
def test_companies_house_enrolment_change_company_name(
    mock_get_is_enrolled, client, submit_companies_house_step, steps_data, user
):
    mock_get_is_enrolled.return_value = True

    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH])
    assert response.status_code == 302

    response = client.get(response.url)
    assert response.context_data['contact_us_url'] == urls.domestic.CONTACT_US / 'domestic'

    # given the user has submitted their company details
    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )
    assert response.status_code == 302

    # when they go back and changed their company
    response = submit_companies_house_step(
        data={'company_name': 'Bar corp', 'company_number': '12345679'}, step_name=constants.COMPANY_SEARCH
    )
    assert response.status_code == 302

    # then the company name is not overwritten by the previously submitted one.
    response = client.get(response.url)

    assert response.context_data['form']['company_name'].data == 'Example corp'
    assert response.context_data['is_enrolled']
    assert response.context_data['contact_us_url'] == urls.domestic.CONTACT_US / 'domestic'


def test_companies_house_enrolment_expose_company(
    client,
    submit_companies_house_step,
    steps_data,
    user,
):
    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH])
    assert response.status_code == 302

    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.context_data['company'] == {
        'company_name': 'Example corp',
        'company_number': '12345678',
        'date_of_creation': '2001-01-20',
        'postal_code': 'EDG 4DF',
        'address': '555 fake street, London, EDG 4DF',
        'address_line_1': '555 fake street',
        'address_line_2': 'London',
        'address_line_3': 'EDG 4DF',
        'sectors': ['AEROSPACE'],
        'sic': '',
        'website': '',
    }


def test_companies_house_enrolment_redirect_to_start(client, user):
    client.force_login(user)

    url = reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.ADDRESS_SEARCH})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:enrolment-business-type')


@mock.patch('sso_profile.enrolment.views.helpers.create_company_member')
def test_companies_house_enrolment_submit_end_to_end(
    mock_add_collaborator,
    client,
    submit_companies_house_step,
    mock_enrolment_send,
    mock_get_supplier_profile,
    steps_data,
    session_client_referrer_factory,
    user,
):
    session_client_referrer_factory(urls.domestic.FIND_A_BUYER)
    ingress_url = 'http://testserver/foo/'

    # given the ingress url is set
    response = client.get(
        reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.USER_ACCOUNT}),
        HTTP_REFERER=ingress_url,
        HTTP_HOST='testserver',
    )
    assert response.status_code == 200

    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH])
    assert response.status_code == 302

    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )
    assert response.status_code == 302

    response = submit_companies_house_step(data=steps_data[constants.PERSONAL_INFO], step_name=constants.PERSONAL_INFO)
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 200
    assert response.template_name == views.CompaniesHouseEnrolmentView.templates[constants.FINISHED]
    assert response.context_data['ingress_url'] == ingress_url

    assert mock_enrolment_send.call_count == 1
    assert mock_enrolment_send.call_args == mock.call(
        {
            'sso_id': 1,
            'company_email': 'jim@example.com',  # /PS-IGNORE
            'contact_email_address': 'jim@example.com',  # /PS-IGNORE
            'company_name': 'Example corp',
            'company_number': '12345678',
            'date_of_creation': '2001-01-20',
            'postal_code': 'EDG 4DF',
            'address_line_1': '555 fake street',
            'address_line_2': 'London',
            'sectors': ['AEROSPACE'],
            'name': None,
            'job_title': 'Exampler',
            'phone_number': '1232342',
            'company_type': 'COMPANIES_HOUSE',
        }
    )


@mock.patch('sso_profile.enrolment.views.helpers.create_company_member')
def test_companies_house_enrolment_submit_end_to_end_logged_in(
    mock_add_collaborator, client, captcha_stub, submit_companies_house_step, mock_enrolment_send, steps_data, user
):
    client.force_login(user)

    url = reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url)
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH], step_name=constants.COMPANY_SEARCH)

    assert response.status_code == 302

    step = resolve(response.url).kwargs['step']
    response = submit_companies_house_step({'company_name': 'Example corp', 'sectors': 'AEROSPACE'}, step_name=step)
    assert response.status_code == 302

    step = resolve(response.url).kwargs['step']
    response = submit_companies_house_step(
        {**steps_data[constants.PERSONAL_INFO], 'terms_agreed': True},  # not agreed during user account creation
        step_name=step,
    )
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 200
    assert response.template_name == views.CompaniesHouseEnrolmentView.templates[constants.FINISHED]
    assert mock_enrolment_send.call_count == 1
    assert mock_enrolment_send.call_args == mock.call(
        {
            'address_line_1': '555 fake street',
            'address_line_2': 'London',
            'company_email': 'jim@example.com',  # /PS-IGNORE
            'company_name': 'Example corp',
            'company_number': '12345678',
            'company_type': 'COMPANIES_HOUSE',
            'contact_email_address': 'jim@example.com',  # /PS-IGNORE
            'date_of_creation': '2001-01-20',
            'job_title': 'Exampler',
            'name': None,
            'phone_number': '1232342',
            'postal_code': 'EDG 4DF',
            'sectors': ['AEROSPACE'],
            'sso_id': 1,
        }
    )


def test_companies_house_enrolment_submit_end_to_end_no_address(
    client, captcha_stub, submit_companies_house_step, mock_enrolment_send, steps_data, user, mock_get_company_profile
):
    client.force_login(user)

    mock_get_company_profile.return_value = {
        'company_number': 'IP345678',
        'company_name': 'Example corp',
        'sic_codes': ['1234'],
        'date_of_creation': '2001-01-20',
        'registered_office_address': {'address_line_1': '555 fake street, London', 'postal_code': 'EDG 4DF'},
        'company_status': 'active',
    }

    url = reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url)

    assert response.status_code == 302

    response = submit_companies_house_step(
        data={'company_name': 'Example corp', 'company_number': 'IP12345678'}, step_name=constants.COMPANY_SEARCH
    )

    assert response.status_code == 302

    response = client.get(response.url)
    assert response.context_data['is_in_companies_house'] is True

    response = submit_companies_house_step(
        data={'company_name': 'Example corp', 'postal_code': 'EDG 4DF', 'address': '555 fake street, London'},
        step_name=constants.ADDRESS_SEARCH,
    )
    assert response.status_code == 302

    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )

    assert response.status_code == 302

    response = submit_companies_house_step(
        data={**steps_data[constants.PERSONAL_INFO], 'terms_agreed': True}, step_name=constants.PERSONAL_INFO
    )

    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 200
    assert response.template_name == views.CompaniesHouseEnrolmentView.templates[constants.FINISHED]
    assert mock_enrolment_send.call_count == 1
    assert mock_enrolment_send.call_args == mock.call(
        {
            'address_line_1': '555 fake street',
            'address_line_2': 'London',
            'company_email': 'jim@example.com',  # /PS-IGNORE
            'company_name': 'Example corp',
            'company_number': 'IP345678',
            'company_type': 'COMPANIES_HOUSE',
            'contact_email_address': 'jim@example.com',  # /PS-IGNORE
            'date_of_creation': '2001-01-20',
            'job_title': 'Exampler',
            'name': None,  # to good way in tests to populate this after login
            'phone_number': '1232342',
            'postal_code': 'EDG 4DF',
            'sectors': ['AEROSPACE'],
            'sso_id': 1,
        }
    )


def test_companies_house_enrolment_suppress_success_page(client, submit_companies_house_step, steps_data, user):
    response = client.get(reverse('sso_profile:enrolment-business-type'), {'business-profile-intent': True})
    assert response.status_code == 200

    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH])
    assert response.status_code == 302

    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )
    assert response.status_code == 302

    response = submit_companies_house_step(data=steps_data[constants.PERSONAL_INFO], step_name=constants.PERSONAL_INFO)
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:business-profile')


@pytest.mark.parametrize('step', [name for name, _ in views.CompaniesHouseEnrolmentView.form_list])
def test_companies_house_enrolment_has_company(client, step, mock_user_has_company, user):
    client.force_login(user)

    mock_user_has_company.return_value = create_response()

    url = reverse('sso_profile:enrolment-companies-house', kwargs={'step': step})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:about')


@pytest.mark.parametrize('step', [name for name, _ in views.CompaniesHouseEnrolmentView.form_list])
def test_companies_house_enrolment_has_company_error(client, step, mock_user_has_company, user):
    client.force_login(user)

    mock_user_has_company.return_value = create_response(status_code=500)

    url = reverse('sso_profile:enrolment-companies-house', kwargs={'step': step})

    with pytest.raises(HTTPError):
        client.get(url)


@mock.patch('directory_forms_api_client.client.forms_api_client.submit_generic')
@mock.patch('sso_profile.enrolment.views.helpers.create_company_member')
@mock.patch('sso.models.BusinessSSOUser.role')
def test_companies_house_enrolment_submit_end_to_end_company_has_account(
    mock_user_role,
    mock_add_collaborator,
    mock_gov_notify,
    client,
    steps_data,
    submit_companies_house_step,
    mock_get_company_admins,
    mock_enrolment_send,
    mock_validate_company_number,
    user,
):
    mock_validate_company_number.return_value = create_response(status_code=400)

    mock_user_role.return_value = user_roles.MEMBER

    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH])
    assert response.status_code == 302

    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )
    assert response.status_code == 302

    response = submit_companies_house_step(data=steps_data[constants.PERSONAL_INFO], step_name=constants.PERSONAL_INFO)
    assert response.status_code == 302

    response = client.get(response.url)

    # Redirects to business profile for 2nd company `member` user
    assert response.status_code == 302

    assert mock_add_collaborator.call_count == 1
    assert mock_add_collaborator.call_args == mock.call(
        sso_session_id='123',
        data={
            'sso_id': 1,
            'name': None,
            'company': '12345678',
            'company_email': 'jim@example.com',  # /PS-IGNORE
            'mobile_number': '1232342',
        },
    )

    assert mock_get_company_admins.call_count == 1
    assert mock_gov_notify.call_count == 2


@mock.patch('directory_forms_api_client.client.forms_api_client.submit_generic')
@mock.patch('sso_profile.enrolment.views.helpers.create_company_member')
@mock.patch('sso_profile.enrolment.views.helpers.get_is_enrolled')
@mock.patch('sso_profile.business_profile.helpers.has_editor_admin_request')
def test_companies_house_enrolment_submit_end_to_end_company_second_user(
    mock_has_editor_admin_request,
    mock_get_is_enrolled,
    mock_add_collaborator,
    mock_gov_notify,
    client,
    steps_data,
    submit_companies_house_step,
    mock_get_company_admins,
    mock_enrolment_send,
    mock_validate_company_number,
    mock_retrieve_member_supplier,
    user,
):
    mock_validate_company_number.return_value = create_response(status_code=400)

    mock_get_is_enrolled.return_value = True

    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH])
    assert response.status_code == 302

    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )
    assert response.status_code == 302

    response = submit_companies_house_step(data=steps_data[constants.PERSONAL_INFO], step_name=constants.PERSONAL_INFO)
    assert response.status_code == 302

    response = client.get(response.url, follow=True)

    # Redirects to business profile for 2nd company `member` user
    assert response.status_code == 200
    messages = list(str(message) for message in response.context['messages'])
    assert len(messages) == 1

    for message in messages:
        assert message == 'You are now linked to the profile.'

    assert mock_add_collaborator.call_count == 1
    assert mock_add_collaborator.call_args == mock.call(
        sso_session_id='123',
        data={
            'sso_id': 1,
            'name': None,
            'company': '12345678',
            'company_email': 'jim@example.com',  # /PS-IGNORE
            'mobile_number': '1232342',
        },
    )

    assert mock_get_company_admins.call_count == 1
    assert mock_gov_notify.call_count == 2

    assert mock_has_editor_admin_request.call_count == 0


@mock.patch('directory_forms_api_client.client.forms_api_client.submit_generic')
@mock.patch('sso_profile.enrolment.views.helpers.create_company_member')
@mock.patch('sso.models.BusinessSSOUser.role')
def test_companies_house_enrolment_submit_end_to_end_company_has_user_profile(
    mock_user_role,
    mock_add_collaborator,
    mock_gov_notify,
    client,
    steps_data,
    submit_companies_house_step,
    mock_enrolment_send,
    mock_get_company_admins,
    mock_validate_company_number,
    user,
):
    mock_validate_company_number.return_value = create_response(status_code=400)
    user.has_user_profile = True
    user.first_name = 'Foo'
    user.last_name = 'Bar'

    mock_user_role.return_value = user_roles.ADMIN

    client.force_login(user)

    response = submit_companies_house_step(
        data=steps_data[constants.COMPANY_SEARCH], step_name=constants.COMPANY_SEARCH
    )
    assert response.status_code == 302

    response = submit_companies_house_step(
        data=steps_data[BUSINESS_INFO_COMPANIES_HOUSE], step_name=constants.BUSINESS_INFO
    )
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 302
    assert mock_enrolment_send.call_count == 0
    assert mock_add_collaborator.call_count == 1
    assert mock_add_collaborator.call_args == mock.call(
        sso_session_id='123',
        data={
            'sso_id': 1,
            'name': 'Foo Bar',
            'company': '12345678',
            'company_email': 'jim@example.com',  # /PS-IGNORE
            'mobile_number': '',
        },
    )

    assert mock_get_company_admins.call_count == 1
    assert mock_gov_notify.call_count == 2


def test_verification_missing_url(submit_companies_house_step, client, steps_data):
    response = submit_companies_house_step(steps_data[constants.USER_ACCOUNT])
    response = client.get(response.url)

    verification_missing_url = urls.domestic.CONTACT_US / 'triage/great-account/verification-missing/'

    assert response.context_data['verification_missing_url'] == verification_missing_url


def test_user_has_company_redirect_on_start(client, mock_user_has_company, user):
    client.force_login(user)
    mock_user_has_company.return_value = create_response()

    url = reverse('sso_profile:enrolment-start')
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:business-profile')


def test_user_has_no_company_redirect_on_start(client, mock_user_has_company, user):
    client.force_login(user)
    mock_user_has_company.return_value = create_response(status_code=404)

    url = reverse('sso_profile:enrolment-start')
    response = client.get(url)

    assert response.status_code == 200


@pytest.mark.parametrize('company_type', company_types)
def test_create_user_enrolment(client, steps_data, submit_step_builder, company_type):
    submit_step = submit_step_builder(company_type)
    response = submit_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302


@pytest.mark.parametrize(
    'company_type,form_url_name',
    zip(
        company_types,
        [
            'sso_profile:enrolment-companies-house',
            'sso_profile:enrolment-sole-trader',
        ],
    ),
)
def test_create_user_enrolment_already_exists(
    company_type, form_url_name, steps_data, mock_create_user, submit_step_builder, mock_notify_already_registered
):
    mock_create_user.return_value = create_response(
        json_body={'email': ['already registered']}, status_code=400
    )  # /PS-IGNORE

    submit_step = submit_step_builder(company_type)

    response = submit_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302
    assert mock_notify_already_registered.call_count == 1
    assert mock_notify_already_registered.call_args == mock.call(
        email='jim@example.com', form_url=reverse(form_url_name, kwargs={'step': constants.USER_ACCOUNT})  # /PS-IGNORE
    )


@pytest.mark.parametrize(
    'company_type,form_url_name',
    zip(
        company_types,
        [
            'sso_profile:enrolment-companies-house',
            'sso_profile:enrolment-sole-trader',
        ],
    ),
)
def test_create_user_enrolment_bad_password(
    company_type, form_url_name, steps_data, mock_create_user, submit_step_builder, client
):
    mock_create_user.return_value = create_response(json_body={'password': ['something is wrong']}, status_code=400)

    submit_step = submit_step_builder(company_type)

    response = submit_step(steps_data[constants.USER_ACCOUNT])

    assert response.status_code == 302

    response = client.get(response.url)
    assert response.context_data['form'].errors == {'password': ['something is wrong']}


@pytest.mark.parametrize(
    'company_type,form_url_name',
    zip(company_types, ['sso_profile:enrolment-companies-house', 'sso_profile:enrolment-sole-trader']),
)
def test_create_user_enrolment_bad_then_good_password(
    company_type, form_url_name, steps_data, mock_create_user, submit_step_builder, client
):
    mock_create_user.return_value = create_response(json_body={'password': ['something is wrong']}, status_code=400)

    submit_step = submit_step_builder(company_type)

    response = submit_step(steps_data[constants.USER_ACCOUNT])

    assert response.status_code == 302

    response = client.get(response.url)
    assert response.context_data['form'].errors == {'password': ['something is wrong']}

    mock_create_user.return_value = create_response(
        {'email': 'test@test.com', 'verification_code': '123456'}  # /PS-IGNORE
    )  # /PS-IGNORE

    response = submit_step(data=steps_data[constants.USER_ACCOUNT], step_name=constants.USER_ACCOUNT)

    assert response.status_code == 302
    assert constants.USER_ACCOUNT not in response.url


@pytest.mark.parametrize('company_type', company_types)
@freeze_time('2012-01-14 12:00:02')
def test_user_verification_passes_cookies(company_type, submit_step_builder, client, steps_data):
    submit_step = submit_step_builder(company_type)

    response = submit_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    assert str(response.cookies['debug_sso_session_cookie']) == (
        'Set-Cookie: debug_sso_session_cookie=foo-bar; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; HttpOnly; Max-Age=1209600; '
        'Path=/; Secure'
    )
    assert str(response.cookies['sso_display_logged_in']) == (
        'Set-Cookie: sso_display_logged_in=true; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; Max-Age=1209600; Path=/'
    )


@pytest.mark.parametrize('company_type', company_types)
@freeze_time('2012-01-14 12:00:02')
def test_user_verification_manual_passes_cookies(company_type, submit_step_builder, client):
    submit_step = submit_step_builder(company_type)

    response = submit_step(
        data={'email': 'test@test.com', 'code': '12345'}, step_name=constants.VERIFICATION  # /PS-IGNORE
    )  # /PS-IGNORE
    assert response.status_code == 302

    assert str(response.cookies['debug_sso_session_cookie']) == (
        'Set-Cookie: debug_sso_session_cookie=foo-bar; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; HttpOnly; Max-Age=1209600; '
        'Path=/; Secure'
    )
    assert str(response.cookies['sso_display_logged_in']) == (
        'Set-Cookie: sso_display_logged_in=true; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; Max-Age=1209600; Path=/'
    )


@pytest.mark.parametrize('company_type', company_types)
def test_confirm_user_verify_code_incorrect_code(
    client, company_type, submit_step_builder, mock_confirm_verification_code, steps_data
):
    submit_step = submit_step_builder(company_type)

    mock_confirm_verification_code.return_value = create_response(status_code=400, json_body={'code': ['Invalid code']})

    response = submit_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_step(steps_data[constants.VERIFICATION])

    assert response.status_code == 302

    response = client.get(response.url)
    assert response.context_data['form'].errors['code'] == ['Invalid code']


@pytest.mark.parametrize('company_type', company_types)
def test_confirm_user_verify_code_manual_email(
    company_type, submit_step_builder, mock_confirm_verification_code, steps_data, client
):
    mock_confirm_verification_code.return_value = create_response(status_code=400, json_body={'code': ['Invalid code']})
    submit_step = submit_step_builder(company_type)

    response = submit_step(
        data={'email': 'test@test.com', 'code': '12345'}, step_name=constants.VERIFICATION  # /PS-IGNORE
    )  # /PS-IGNORE

    assert response.status_code == 302

    response = client.get(response.url)

    assert response.context_data['form'].is_valid() is False
    assert response.context_data['form'].errors['code'] == ['Invalid code']


@pytest.mark.parametrize('company_type', company_types)
def test_confirm_user_verify_code_remote_error(
    company_type, submit_step_builder, mock_confirm_verification_code, steps_data
):
    submit_step = submit_step_builder(company_type)

    mock_confirm_verification_code.return_value = create_response(status_code=500)

    response = submit_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    with pytest.raises(HTTPError):
        submit_step(steps_data[constants.VERIFICATION])


@pytest.mark.parametrize('company_type', company_types)
def test_confirm_user_verify_code(
    client, company_type, submit_step_builder, mock_confirm_verification_code, steps_data, user
):
    submit_step = submit_step_builder(company_type)

    response = submit_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_step(steps_data[constants.VERIFICATION])

    client.force_login(user)

    assert response.status_code == 302
    assert mock_confirm_verification_code.call_count == 1
    assert mock_confirm_verification_code.call_args == mock.call(
        {'email': 'jim@example.com', 'code': '12345'}  # /PS-IGNORE
    )  # /PS-IGNORE


def test_confirm_user_resend_verification_code(
    mock_regenerate_verification_code,
    mock_send_verification_code_email,
    submit_resend_verification_house_step,
    steps_data,
):
    response = submit_resend_verification_house_step(steps_data[constants.RESEND_VERIFICATION])
    assert response.status_code == 302

    assert mock_regenerate_verification_code.call_count == 1
    assert mock_regenerate_verification_code.call_args == mock.call({'email': 'jim@example.com'})  # /PS-IGNORE

    assert mock_send_verification_code_email.call_count == 1
    assert mock_send_verification_code_email.call_args == mock.call(
        email='jim@example.com',  # /PS-IGNORE
        form_url='/profile/enrol/resend-verification/resend/',
        verification_code={'code': '12345', 'expiration_date': '2018-01-17T12:00:01Z'},
        verification_link='http://testserver/profile/enrol/resend-verification/verification/',
        resend_verification_link='http://testserver/profile/enrol/resend-verification/resend/',
    )


def test_confirm_user_resend_verification_code_user_verified(
    mock_regenerate_verification_code,
    mock_send_verification_code_email,
    submit_resend_verification_house_step,
    steps_data,
):
    mock_regenerate_verification_code.return_value = create_response(status_code=404)

    response = submit_resend_verification_house_step(steps_data[constants.RESEND_VERIFICATION])

    assert response.status_code == 302

    assert mock_regenerate_verification_code.call_count == 1
    assert mock_regenerate_verification_code.call_args == mock.call({'email': 'jim@example.com'})  # /PS-IGNORE

    assert mock_send_verification_code_email.call_count == 0


def test_confirm_user_resend_verification_code_no_user(
    mock_regenerate_verification_code,
    mock_send_verification_code_email,
    submit_resend_verification_house_step,
    steps_data,
):
    mock_regenerate_verification_code.return_value = create_response(status_code=404)

    response = submit_resend_verification_house_step(steps_data[constants.RESEND_VERIFICATION])

    assert response.status_code == 302

    assert mock_regenerate_verification_code.call_count == 1
    assert mock_regenerate_verification_code.call_args == mock.call({'email': 'jim@example.com'})  # /PS-IGNORE

    assert mock_send_verification_code_email.call_count == 0


@freeze_time('2012-01-14 12:00:02')
def test_confirm_user_resend_verification_code_complete(client, submit_resend_verification_house_step, steps_data):
    response = submit_resend_verification_house_step(steps_data[constants.RESEND_VERIFICATION])

    assert response.status_code == 302

    response = submit_resend_verification_house_step(
        steps_data[constants.VERIFICATION], step_name=resolve(response.url).kwargs['step']
    )
    assert response.status_code == 302
    assert response.url == reverse('sso_profile:enrolment-business-type')

    assert str(response.cookies['debug_sso_session_cookie']) == (
        'Set-Cookie: debug_sso_session_cookie=foo-bar; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; HttpOnly; Max-Age=1209600; '
        'Path=/; Secure'
    )
    assert str(response.cookies['sso_display_logged_in']) == (
        'Set-Cookie: sso_display_logged_in=true; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; Max-Age=1209600; Path=/'
    )


@freeze_time('2012-01-14 12:00:02')
def test_confirm_user_resend_verification_code_choice_companies_house(
    session_client_company_factory, submit_resend_verification_house_step, steps_data
):
    session_client_company_factory(constants.COMPANIES_HOUSE_COMPANY)

    response = submit_resend_verification_house_step(steps_data[constants.RESEND_VERIFICATION])

    assert response.status_code == 302

    response = submit_resend_verification_house_step(
        steps_data[constants.VERIFICATION], step_name=resolve(response.url).kwargs['step']
    )

    assert response.status_code == 302

    assert response.url == reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.USER_ACCOUNT})

    assert str(response.cookies['debug_sso_session_cookie']) == (
        'Set-Cookie: debug_sso_session_cookie=foo-bar; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; HttpOnly; Max-Age=1209600; '
        'Path=/; Secure'
    )
    assert str(response.cookies['sso_display_logged_in']) == (
        'Set-Cookie: sso_display_logged_in=true; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; Max-Age=1209600; Path=/'
    )


@freeze_time('2012-01-14 12:00:02')
def test_confirm_user_resend_verification_code_choice_non_companies_house(
    session_client_company_factory, submit_resend_verification_house_step, steps_data
):
    session_client_company_factory(constants.NON_COMPANIES_HOUSE_COMPANY)

    response = submit_resend_verification_house_step(steps_data[constants.RESEND_VERIFICATION])

    assert response.status_code == 302

    response = submit_resend_verification_house_step(
        steps_data[constants.VERIFICATION], step_name=resolve(response.url).kwargs['step']
    )

    assert response.status_code == 302

    assert response.url == reverse('sso_profile:enrolment-sole-trader', kwargs={'step': constants.USER_ACCOUNT})

    assert str(response.cookies['debug_sso_session_cookie']) == (
        'Set-Cookie: debug_sso_session_cookie=foo-bar; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; HttpOnly; Max-Age=1209600; '
        'Path=/; Secure'
    )
    assert str(response.cookies['sso_display_logged_in']) == (
        'Set-Cookie: sso_display_logged_in=true; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; Max-Age=1209600; Path=/'
    )


@freeze_time('2012-01-14 12:00:02')
def test_confirm_user_resend_verification_code_choice_individual(
    session_client_company_factory, submit_resend_verification_house_step, steps_data
):
    session_client_company_factory(constants.NOT_COMPANY)

    response = submit_resend_verification_house_step(steps_data[constants.RESEND_VERIFICATION])

    assert response.status_code == 302

    response = submit_resend_verification_house_step(
        steps_data[constants.VERIFICATION], step_name=resolve(response.url).kwargs['step']
    )

    assert response.status_code == 302

    assert response.url == reverse('sso_profile:enrolment-individual', kwargs={'step': constants.USER_ACCOUNT})

    assert str(response.cookies['debug_sso_session_cookie']) == (
        'Set-Cookie: debug_sso_session_cookie=foo-bar; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; HttpOnly; Max-Age=1209600; '
        'Path=/; Secure'
    )
    assert str(response.cookies['sso_display_logged_in']) == (
        'Set-Cookie: sso_display_logged_in=true; Domain=.trade.great; '
        'expires=Thu, 07-Mar-2019 10:17:38 GMT; Max-Age=1209600; Path=/'
    )


def test_confirm_user_resend_verification_logged_in(client, user):
    client.force_login(user)

    url = reverse('sso_profile:resend-verification', kwargs={'step': constants.RESEND_VERIFICATION})

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:about')


def test_confirm_user_resend_verification_context_urls(client):
    url = reverse('sso_profile:resend-verification', kwargs={'step': constants.RESEND_VERIFICATION})

    response = client.get(url)

    missing_url = urls.domestic.CONTACT_US / 'triage/great-account/verification-missing/'
    contact_url = urls.domestic.CONTACT_US / 'domestic/'

    assert response.status_code == 200
    assert response.context_data['verification_missing_url'] == missing_url
    assert response.context_data['contact_url'] == contact_url


def test_non_companies_house_enrolment_expose_company(client, submit_non_companies_house_step, steps_data, user):
    response = submit_non_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_non_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_non_companies_house_step(steps_data[BUSINESS_INFO_NON_COMPANIES_HOUSE])
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.context_data['company'] == {
        'company_type': 'SOLE_TRADER',
        'company_name': 'Test company',
        'postal_code': 'EEA 3AD',
        'address': '555 fake street\nLondon\nEEA 3AD',
        'address_line_1': '555 fake street',
        'address_line_2': 'London',
        'sectors': ['AEROSPACE'],
        'website': '',
    }


def test_anonymouse_user_redirected(client):
    url = reverse('sso_profile:enrolment-sole-trader', kwargs={'step': constants.PERSONAL_INFO})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:enrolment-start')


def test_non_companies_house_enrolment_redirect_to_start(client, user):
    client.force_login(user)

    url = reverse('sso_profile:enrolment-sole-trader', kwargs={'step': constants.PERSONAL_INFO})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:enrolment-business-type')


def test_non_companies_house_enrolment_submit_end_to_end_logged_in(
    client, submit_non_companies_house_step, steps_data, mock_enrolment_send, user
):
    ingress_url = 'http://testserver/foo/'

    # given the ingress url is set
    response = client.get(
        reverse('sso_profile:enrolment-sole-trader', kwargs={'step': constants.USER_ACCOUNT}),
        HTTP_REFERER=ingress_url,
        HTTP_HOST='testserver',
    )

    client.force_login(user)
    url = reverse('sso_profile:enrolment-sole-trader', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url)

    assert response.status_code == 302

    response = submit_non_companies_house_step(
        steps_data[BUSINESS_INFO_NON_COMPANIES_HOUSE], step_name=resolve(response.url).kwargs['step']
    )

    assert response.status_code == 302

    response = submit_non_companies_house_step(
        {**steps_data[constants.PERSONAL_INFO], 'terms_agreed': True}, step_name=resolve(response.url).kwargs['step']
    )
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 200
    assert response.template_name == views.NonCompaniesHouseEnrolmentView.templates[constants.FINISHED]
    assert response.context_data['ingress_url'] == ingress_url
    assert mock_enrolment_send.call_count == 1
    assert mock_enrolment_send.call_args == mock.call(
        {
            'sso_id': 1,
            'company_email': 'jim@example.com',  # /PS-IGNORE
            'contact_email_address': 'jim@example.com',  # /PS-IGNORE
            'company_type': 'SOLE_TRADER',
            'company_name': 'Test company',
            'sectors': ['AEROSPACE'],
            'postal_code': 'EEA 3AD',
            'address_line_1': '555 fake street',
            'address_line_2': 'London',
            'job_title': 'Exampler',
            'phone_number': '1232342',
            'name': None,
        }
    )


def test_non_companies_house_enrolment_has_user_profile(client, submit_non_companies_house_step, steps_data, user):
    user.has_user_profile = True
    client.force_login(user)

    url = reverse('sso_profile:enrolment-sole-trader', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url)

    assert response.status_code == 302

    response = submit_non_companies_house_step(
        steps_data[BUSINESS_INFO_NON_COMPANIES_HOUSE], step_name=resolve(response.url).kwargs['step']
    )

    assert response.status_code == 302

    response = client.get(response.url)
    assert response.status_code == 200
    assert response.template_name == views.NonCompaniesHouseEnrolmentView.templates[constants.FINISHED]


def test_non_companies_house_enrolment_suppress_success(client, submit_non_companies_house_step, steps_data, user):
    response = client.get(reverse('sso_profile:enrolment-business-type'), {'business-profile-intent': True})
    assert response.status_code == 200

    response = submit_non_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_non_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_non_companies_house_step(steps_data[BUSINESS_INFO_NON_COMPANIES_HOUSE])
    assert response.status_code == 302

    response = submit_non_companies_house_step({**steps_data[constants.PERSONAL_INFO], 'terms_agreed': True})
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:business-profile')


NON_COMPANIES_HOUSE_STEPS = [name for name, _ in views.NonCompaniesHouseEnrolmentView.form_list]


def test_non_companies_house_enrolment_exopps_intent(client, submit_non_companies_house_step, steps_data, user):
    client.defaults['HTTP_REFERER'] = 'http://testserver.com/foo/'
    response = client.get(reverse('sso_profile:enrolment-business-type'), {'export-opportunity-intent': True})

    assert response.status_code == 200

    response = submit_non_companies_house_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_non_companies_house_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_non_companies_house_step(steps_data[BUSINESS_INFO_NON_COMPANIES_HOUSE])
    assert response.status_code == 302

    response = submit_non_companies_house_step({**steps_data[constants.PERSONAL_INFO], 'terms_agreed': True})

    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 302
    assert response.url == 'http://testserver.com/foo/'


@pytest.mark.parametrize('step', NON_COMPANIES_HOUSE_STEPS)
def test_non_companies_house_enrolment_has_company(client, step, mock_user_has_company, user):
    client.force_login(user)

    mock_user_has_company.return_value = create_response()

    url = reverse('sso_profile:enrolment-sole-trader', kwargs={'step': step})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:about')


@pytest.mark.parametrize('step', NON_COMPANIES_HOUSE_STEPS)
def test_non_companies_house_enrolment_has_company_error(client, step, mock_user_has_company, user):
    client.force_login(user)

    mock_user_has_company.return_value = create_response(status_code=500)

    url = reverse('sso_profile:enrolment-sole-trader', kwargs={'step': step})

    with pytest.raises(HTTPError):
        client.get(url)


def test_claim_preverified_no_key(client, submit_pre_verified_step, steps_data, user):
    response = submit_pre_verified_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_pre_verified_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    url = reverse('sso_profile:enrolment-pre-verified', kwargs={'step': constants.PERSONAL_INFO})
    response = client.get(url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:enrolment-start')


def test_claim_preverified_bad_key(client, mock_retrieve_preverified_company):
    mock_retrieve_preverified_company.return_value = create_response(status_code=404)

    url = reverse('sso_profile:enrolment-pre-verified', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url, {'key': '123'})

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:enrolment-start')


def test_claim_preverified_exposes_company(
    submit_pre_verified_step, mock_claim_company, client, steps_data, preverified_company_data, user
):
    url = reverse('sso_profile:enrolment-pre-verified', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url, {'key': 'some-key'})

    assert response.status_code == 200

    response = submit_pre_verified_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_pre_verified_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    url = reverse('sso_profile:enrolment-pre-verified', kwargs={'step': constants.PERSONAL_INFO})
    response = client.get(url)

    assert response.status_code == 200
    assert response.context_data['company'] == preverified_company_data


def test_claim_preverified_success(submit_pre_verified_step, mock_claim_company, client, steps_data, user):
    url = reverse('sso_profile:enrolment-pre-verified', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url, {'key': 'some-key'})

    assert response.status_code == 200

    response = submit_pre_verified_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_pre_verified_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_pre_verified_step(steps_data[constants.PERSONAL_INFO])
    assert response.status_code == 302

    user.has_user_profile = True
    user.first_name = 'Foo'
    user.last_name = 'Example'
    client.force_login(user)

    response = client.get(response.url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:business-profile')
    assert mock_claim_company.call_count == 1
    assert mock_claim_company.call_args == mock.call(data={'name': 'Foo Example'}, key='some-key', sso_session_id='123')


def test_claim_preverified_success_logged_in(
    submit_pre_verified_step, mock_create_user_profile, client, steps_data, user, mock_claim_company
):
    user.has_user_profile = True
    user.first_name = 'Foo'
    user.last_name = 'Example'
    client.force_login(user)

    url = reverse('sso_profile:enrolment-pre-verified', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url, {'key': 'some-key'})

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:business-profile')
    assert mock_create_user_profile.call_count == 0
    assert mock_claim_company.call_count == 1
    assert mock_claim_company.call_args == mock.call(data={'name': 'Foo Example'}, key='some-key', sso_session_id='123')


@pytest.mark.parametrize(
    'is_anon,expected',
    (
        (
            True,
            [
                constants.PROGRESS_STEP_LABEL_BUSINESS_TYPE,
                constants.PROGRESS_STEP_LABEL_USER_ACCOUNT,
                constants.PROGRESS_STEP_LABEL_VERIFICATION,
                constants.PROGRESS_STEP_LABEL_PERSONAL_INFO,
            ],
        ),
        (False, [constants.PROGRESS_STEP_LABEL_BUSINESS_TYPE, constants.PROGRESS_STEP_LABEL_PERSONAL_INFO]),
    ),
)
def test_steps_list_mixin(is_anon, expected, rf, settings, user):
    class TestView(mixins.StepsListMixin, TemplateView):
        template_name = 'domestic/base.html'

        steps_list_labels = [
            constants.PROGRESS_STEP_LABEL_BUSINESS_TYPE,
            constants.PROGRESS_STEP_LABEL_USER_ACCOUNT,
            constants.PROGRESS_STEP_LABEL_VERIFICATION,
            constants.PROGRESS_STEP_LABEL_PERSONAL_INFO,
        ]

    request = rf.get('/')
    request.user = AnonymousUser() if is_anon else user
    view = TestView.as_view()

    response = view(request)
    assert response.context_data['step_labels'] == expected


@pytest.mark.parametrize('is_anon', (True, False))
def test_wizard_progress_indicator_mixin(is_anon, rf, settings, client, user):
    class TestView(mixins.ProgressIndicatorMixin, NamedUrlSessionWizardView):
        def get_template_names(self):
            return ['enrolment/user-account-resend-verification.html']

        form_list = ((constants.USER_ACCOUNT, forms.UserAccount), (constants.COMPANY_SEARCH, forms.UserAccount))

        progress_conf = helpers.ProgressIndicatorConf(
            step_counter_user={constants.USER_ACCOUNT: 2}, step_counter_anon={constants.USER_ACCOUNT: 2}
        )

    request = rf.get('/')
    request.session = client.session
    request.user = AnonymousUser() if is_anon else user
    view = TestView.as_view(url_name='sso_profile:enrolment-companies-house')
    response = view(request, step=constants.USER_ACCOUNT)

    assert response.context_data['step_number'] == 2


def test_individual_enrolment_steps(client, submit_individual_step, steps_data, user):
    response = submit_individual_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_individual_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_individual_step(steps_data[constants.PERSONAL_INFO])
    assert response.status_code == 302


def test_individual_enrolment_submit_end_to_end(
    client, submit_individual_step, user, mock_create_user_profile, steps_data, session_client_referrer_factory
):
    session_client_referrer_factory(urls.domestic.FIND_A_BUYER)
    response = submit_individual_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_individual_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_individual_step(steps_data[constants.PERSONAL_INFO])
    assert response.status_code == 302

    client.get(response.url)

    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        data={'first_name': 'Foo', 'last_name': 'Example', 'job_title': 'Exampler', 'mobile_phone_number': '1232342'},
        sso_session_id='123',
    )


def test_individual_enrolment_submit_end_to_end_logged_in(
    client, submit_individual_step, user, mock_create_user_profile, steps_data
):
    client.force_login(user)

    url = reverse('sso_profile:enrolment-individual', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url)
    assert response.status_code == 302

    step = resolve(response.url).kwargs['step']

    assert step == constants.PERSONAL_INFO

    response = submit_individual_step({**steps_data[constants.PERSONAL_INFO], 'terms_agreed': True}, step_name=step)
    assert response.status_code == 302

    response = client.get(response.url)
    assert response.status_code == 200

    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        data={'first_name': 'Foo', 'last_name': 'Example', 'job_title': 'Exampler', 'mobile_phone_number': '1232342'},
        sso_session_id='123',
    )


def test_overseas_business_enrolmnet(client):
    url = reverse('sso_profile:enrolment-overseas-business')

    response = client.get(url)

    assert response.status_code == 200


def test_enrolment_individual_interstitial_anonymous_user(client):
    expected = reverse('sso_profile:enrolment-individual', kwargs={'step': constants.PERSONAL_INFO})
    url = reverse('sso_profile:enrolment-individual-interstitial')

    response = client.get(url)

    assert response.status_code == 302
    assert response.url == expected


def test_enrolment_individual_interstitial_create_business_profile_intent(client, user):
    response = client.get(reverse('sso_profile:enrolment-business-type'), {'business-profile-intent': True})
    assert response.status_code == 200

    expected = reverse('sso_profile:enrolment-individual', kwargs={'step': constants.USER_ACCOUNT})
    url = reverse('sso_profile:enrolment-individual-interstitial')

    response = client.get(url)

    assert response.status_code == 200
    assert expected.encode() in response.content


expose_user_jourey_urls = (
    reverse('sso_profile:enrolment-individual', kwargs={'step': constants.USER_ACCOUNT}),
    reverse('sso_profile:enrolment-pre-verified', kwargs={'step': constants.USER_ACCOUNT}) + '?key=some-key',
    reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.USER_ACCOUNT}),
    reverse('sso_profile:enrolment-sole-trader', kwargs={'step': constants.USER_ACCOUNT}),
    reverse('sso_profile:enrolment-overseas-business'),
    reverse('sso_profile:enrolment-business-type'),
    reverse('sso_profile:enrolment-start'),
)


@pytest.mark.parametrize(
    'intent_write_url', (reverse('sso_profile:enrolment-business-type'), reverse('sso_profile:enrolment-start'))
)
@pytest.mark.parametrize(
    'params,verb',
    (
        ({'backfill-details-intent': True}, mixins.ReadUserIntentMixin.LABEL_BACKFILL_DETAILS),
        ({'business-profile-intent': True}, mixins.ReadUserIntentMixin.LABEL_BUSINESS),
        (
            {'next': 'http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2Fenrol%2F%3Fbusiness-profile-intent%3Dtrue'},
            mixins.ReadUserIntentMixin.LABEL_BUSINESS,
        ),
        (
            {'next': 'http%3A%2F%2Fprofile.trade.great%3A8006%2Fprofile%2Fenrol%2F'},
            mixins.ReadUserIntentMixin.LABEL_ACCOUNT,
        ),
        ({}, mixins.ReadUserIntentMixin.LABEL_ACCOUNT),
    ),
)
@pytest.mark.parametrize('intent_read_url', expose_user_jourey_urls)
def test_expose_user_journey_intent(intent_write_url, intent_read_url, params, client, verb):
    response = client.get(intent_write_url, params)
    assert response.status_code == 200

    response = client.get(intent_read_url)

    assert response.status_code == 200
    assert response.context_data['user_journey_verb'] == verb


@pytest.mark.parametrize('url', expose_user_jourey_urls + (reverse('sso_profile:enrolment-individual-interstitial'),))
def test_expose_user_journey_mixin_logged_in(url, client, user):
    client.force_login(user)

    response = client.get(url)
    # logged in users will be sent away from certain views
    if response.status_code == 302:
        response = client.get(response.url)

    assert response.status_code == 200
    assert response.context_data['user_journey_verb'] == (mixins.ReadUserIntentMixin.LABEL_BUSINESS)


@pytest.mark.parametrize('url', expose_user_jourey_urls)
def test_expose_user_journey_mixin_account_intent(url, client):
    response = client.get(url)
    assert response.status_code == 200
    assert response.context_data['user_journey_verb'] == (mixins.ReadUserIntentMixin.LABEL_ACCOUNT)


def test_collaborator_enrolment_wrong_invite_key(client, mock_collaborator_invite_retrieve):
    mock_collaborator_invite_retrieve.return_value = create_response(status_code=404)

    url = reverse('sso_profile:enrolment-collaboration', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(f'{url}?invite_key=abc')

    assert response.status_code == 200
    assert response.template_name == views.CollaboratorEnrolmentView.templates[constants.INVITE_EXPIRED]


def test_collaborator_enrolment_submit_end_to_end(
    client,
    submit_collaborator_enrolment_step,
    user,
    mock_create_user_profile,
    steps_data,
    mock_collaborator_invite_accept,
):
    url = reverse('sso_profile:enrolment-collaboration', kwargs={'step': constants.USER_ACCOUNT})
    client.get(f'{url}?invite_key=abc')

    response = submit_collaborator_enrolment_step(steps_data[constants.USER_ACCOUNT])
    assert response.status_code == 302

    response = submit_collaborator_enrolment_step(steps_data[constants.VERIFICATION])
    assert response.status_code == 302

    client.force_login(user)

    response = submit_collaborator_enrolment_step(steps_data[constants.PERSONAL_INFO])
    assert response.status_code == 302

    client.get(response.url)

    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        data={'first_name': 'Foo', 'last_name': 'Example', 'job_title': 'Exampler', 'mobile_phone_number': '1232342'},
        sso_session_id='123',
    )
    assert mock_collaborator_invite_accept.call_count == 1
    assert mock_collaborator_invite_accept.call_args == mock.call(invite_key='abc', sso_session_id='123')


def test_collaborator_enrolment_submit_end_to_end_logged_in(
    client,
    submit_collaborator_enrolment_step,
    user,
    mock_create_user_profile,
    steps_data,
    mock_collaborator_invite_accept,
):
    client.force_login(user)

    url = reverse('sso_profile:enrolment-collaboration', kwargs={'step': constants.USER_ACCOUNT})
    client.get(f'{url}?invite_key=abc')

    url = reverse('sso_profile:enrolment-individual', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url)
    assert response.status_code == 302

    step = resolve(response.url).kwargs['step']

    assert step == constants.PERSONAL_INFO

    response = submit_collaborator_enrolment_step(
        {**steps_data[constants.PERSONAL_INFO], 'terms_agreed': True}, step_name=step
    )
    assert response.status_code == 302

    response = client.get(response.url)
    assert response.status_code == 302
    assert response.url == reverse('sso_profile:business-profile')

    assert mock_create_user_profile.call_count == 1
    assert mock_create_user_profile.call_args == mock.call(
        data={'first_name': 'Foo', 'last_name': 'Example', 'job_title': 'Exampler', 'mobile_phone_number': '1232342'},
        sso_session_id='123',
    )
    assert mock_collaborator_invite_accept.call_count == 1
    assert mock_collaborator_invite_accept.call_args == mock.call(invite_key='abc', sso_session_id='123')


def test_collaborator_enrolment_submit_end_to_end_already_has_profile(
    client, user, mock_create_user_profile, mock_collaborator_invite_accept
):
    user.has_user_profile = True
    client.force_login(user)

    url = reverse('sso_profile:enrolment-collaboration', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(f'{url}?invite_key=abc')

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:business-profile')
    assert mock_create_user_profile.call_count == 0
    assert mock_collaborator_invite_accept.call_count == 1
    assert mock_collaborator_invite_accept.call_args == mock.call(invite_key='abc', sso_session_id='123')


@mock.patch('sso_profile.enrolment.views.helpers.create_company_profile')
def test_companies_house_enrolment_submit_invalid_data_with_profile_intent(
    mock_create_company_profile,
    session_client_company_factory,
    session_intent_factory,
    client,
    submit_companies_house_step,
    steps_data,
    user,
):
    client.force_login(user)

    mock_create_company_profile.side_effect = ValidationError('Invalid Business Profile data received')

    session_client_company_factory(constants.COMPANIES_HOUSE_COMPANY)
    session_intent_factory(constants.SESSION_KEY_BUSINESS_PROFILE_INTENT)

    url = reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url)
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH], step_name=constants.COMPANY_SEARCH)

    assert response.status_code == 302

    step = resolve(response.url).kwargs['step']
    response = submit_companies_house_step({'company_name': 'Example corp', 'sectors': 'AEROSPACE'}, step_name=step)
    assert response.status_code == 302

    step = resolve(response.url).kwargs['step']
    response = submit_companies_house_step(
        {**steps_data[constants.PERSONAL_INFO], 'terms_agreed': True},  # not agreed during user account creation
        step_name=step,
    )
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 302
    assert response.url == reverse('sso_profile:business-profile')


@mock.patch('sso_profile.enrolment.views.helpers.create_company_profile')
def test_companies_house_enrolment_submit_invalid_data_with_exopps_intent(
    mock_create_company_profile,
    session_client_company_factory,
    session_intent_factory,
    submit_companies_house_step,
    steps_data,
    user,
    client,
):
    mock_create_company_profile.side_effect = ValidationError('Invalid Business Profile data received')
    session_client_company_factory(constants.COMPANIES_HOUSE_COMPANY)
    session_intent_factory(constants.SESSION_KEY_EXPORT_OPPORTUNITY_INTENT)

    client.force_login(user)

    client.defaults['HTTP_REFERER'] = 'http://testserver.com/foo/'

    url = reverse('sso_profile:enrolment-companies-house', kwargs={'step': constants.USER_ACCOUNT})
    response = client.get(url)
    assert response.status_code == 302

    response = submit_companies_house_step(steps_data[constants.COMPANY_SEARCH], step_name=constants.COMPANY_SEARCH)

    assert response.status_code == 302

    step = resolve(response.url).kwargs['step']
    response = submit_companies_house_step({'company_name': 'Example corp', 'sectors': 'AEROSPACE'}, step_name=step)
    assert response.status_code == 302

    step = resolve(response.url).kwargs['step']
    response = submit_companies_house_step(
        {**steps_data[constants.PERSONAL_INFO], 'terms_agreed': True},  # not agreed during user account creation
        step_name=step,
    )
    assert response.status_code == 302

    response = client.get(response.url)

    assert response.status_code == 302
    assert response.url == 'http://testserver.com/foo/'
