from unittest import mock

import pytest
from django.conf import settings
from django.urls import reverse, reverse_lazy

from directory_sso_api_client import sso_api_client
from international_online_offer.core import helpers, hirings, intents, regions, spends
from international_online_offer.models import CsatFeedback, TriageData, UserData
from sso import helpers as sso_helpers
from tests.helpers import create_response


@pytest.mark.django_db
def test_index(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:index')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_sector(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:sector'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_sector_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:sector') + '?next=change-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_sector_initial(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'sector'},
    )
    url = reverse('international_online_offer:sector')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_sector_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:sector')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'sector_sub': 'RESIDENTS_PROPERTY_MANAGEMENT'})
    assert response.status_code == 302


@pytest.mark.django_db
def test_sector_form_valid_saves_to_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:sector')
    response = client.post(url, {'sector_sub': 'RESIDENTS_PROPERTY_MANAGEMENT'})
    assert response.status_code == 302


@pytest.mark.django_db
def test_triage_sector_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:sector')
    client.post(url, {'sector_sub': 'RESIDENTS_PROPERTY_MANAGEMENT'})
    assert client.session['sector_sub'] == 'RESIDENTS_PROPERTY_MANAGEMENT'


@pytest.mark.django_db
def test_intent(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:intent')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_intent_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:intent') + '?next=change-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_intent_initial(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'intent': [intents.SET_UP_NEW_PREMISES], 'intent_other': ''},
    )
    url = reverse('international_online_offer:intent')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_intent_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:intent')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'intent': intents.SET_UP_NEW_PREMISES, 'intent_other': ''})
    assert response.status_code == 302


@pytest.mark.django_db
def test_intent_form_valid_saves_to_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:intent')
    response = client.post(url, {'intent': intents.SET_UP_NEW_PREMISES, 'intent_other': ''})
    assert response.status_code == 302


@pytest.mark.django_db
def test_triage_intent_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:intent')
    client.post(url, {'intent': [intents.SET_UP_NEW_PREMISES]})
    assert client.session['intent'] == [intents.SET_UP_NEW_PREMISES]
    assert client.session['intent_other'] == ''


@pytest.mark.django_db
def test_location(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_location_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:location') + '?next=change-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_location_initial(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'location': 'location'},
    )
    url = reverse('international_online_offer:location')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_location_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'location': regions.WALES})
    assert response.status_code == 302


@pytest.mark.django_db
def test_location_form_valid_saves_to_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    response = client.post(url, {'location': regions.WALES})
    assert response.status_code == 302


@pytest.mark.django_db
def test_triage_location_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    client.post(url, {'location': regions.WALES})
    assert client.session['location'] == regions.WALES
    assert client.session['location_none'] is False


@pytest.mark.django_db
def test_hiring(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_hiring_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:hiring') + '?next=change-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_hiring_initial(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'hiring': 'hiring'},
    )
    url = reverse('international_online_offer:hiring')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_hiring_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'hiring': hirings.ONE_TO_TEN})
    assert response.status_code == 302


@pytest.mark.django_db
def test_hiring_form_valid_saves_to_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    response = client.post(url, {'hiring': hirings.ONE_TO_TEN})
    assert response.status_code == 302


@pytest.mark.django_db
def test_triage_hiring_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    client.post(url, {'hiring': hirings.ELEVEN_TO_FIFTY})
    assert client.session['hiring'] == hirings.ELEVEN_TO_FIFTY


@pytest.mark.django_db
def test_spend(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_login(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:login')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_signup(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:signup')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_spend_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:spend') + '?next=change-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_spend_initial(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'spend': 'spend'},
    )
    url = reverse('international_online_offer:spend')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_spend_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'spend': spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND})
    assert response.status_code == 302


@pytest.mark.django_db
def test_spend_form_valid_saves_to_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    response = client.post(url, {'spend': spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND})
    assert response.status_code == 302


@pytest.mark.django_db
def test_triage_spend_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    client.post(url, {'spend': spends.TWO_MILLION_ONE_TO_FIVE_MILLION})
    assert client.session['spend'] == spends.TWO_MILLION_ONE_TO_FIVE_MILLION
    assert client.session['spend_other'] == ''


@pytest.mark.django_db
def test_eyb_profile(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:profile')
    user.email = 'test@test.com'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(
    'form_data,expected_query_param,jump_to_link',
    (
        (
            {
                'company_name': 'Department for Business and Trade',
                'company_location': 'DE',
                'full_name': 'New Signup Joe Bloggs',
                'role': 'Director',
                'email': 'joe@bloggs.com',
                'telephone_number': '+447923456789',
                'agree_terms': 'true',
                'agree_info_email': '',
                'landing_timeframe': 'UNDER_SIX_MONTHS',
                'company_website': 'http://www.great.gov.uk',
            },
            '?signup=true',
            '#personalised-guide',
        ),
        (
            {
                'company_name': 'Department for Business and Trade',
                'company_location': 'DE',
                'full_name': 'Existing Joe Bloggs',
                'role': 'Director',
                'email': 'joe@bloggs.com',
                'telephone_number': '+447923456789',
                'agree_terms': 'true',
                'agree_info_email': '',
                'landing_timeframe': 'UNDER_SIX_MONTHS',
                'company_website': 'http://www.great.gov.uk',
            },
            '',
            '',
        ),
    ),
)
@pytest.mark.django_db
def test_profile_new_signup_vs_update(client, settings, user, form_data, expected_query_param, jump_to_link):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:profile') + expected_query_param
    user.email = 'test@test.com'
    client.force_login(user)
    response = client.post(
        url,
        form_data,
    )
    assert response.status_code == 302
    assert (
        response['Location']
        == f"{'/international/expand-your-business-in-the-uk/guide/'}" + expected_query_param + jump_to_link
    )


@pytest.mark.django_db
def test_eyb_profile_initial(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    UserData.objects.create(
        hashed_uuid='123',
        company_name='DBT',
        company_location='France',
        full_name='Joe Bloggs',
        role='Director',
        email='test@test.com',
        telephone_number='07923456787',
        agree_terms=True,
        agree_info_email=False,
    )
    url = reverse('international_online_offer:profile')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_edit_your_answers(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:change-your-answers')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_trade_associations(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:trade-associations')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_feedback(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:feedback')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:contact')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact_with_param(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:contact') + '?next=http://anyurl.com'
    response = client.get(url)
    assert response.status_code == 200


@mock.patch('directory_forms_api_client.actions.ZendeskAction')
@pytest.mark.django_db
def test_contact_submit(mock_action_class, client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:contact')
    response = client.post(
        url,
        {
            'full_name': 'Joe Bloggs',
            'email': 'test@test.com',
            'how_we_can_help': 'Help me please.',
        },
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_csat_feedback(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:csat-feedback')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_csat_feedback_with_session_value(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:csat-feedback')
    CsatFeedback.objects.create(id=1, URL='http://test.com')
    session = client.session
    session['csat_id'] = 1
    session.save()
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_csat_feedback_submit(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:csat-feedback') + '?url=http://testurl.com'
    CsatFeedback.objects.create(id=1, URL='http://test.com')
    session = client.session
    session['csat_id'] = 1
    session['user_journey'] = 'DASHBOARD'
    session.save()
    response = client.post(
        url,
        {
            'satisfaction': 'SATISFIED',
            'user_journey': 'DASHBOARD',
            'experience': ['I_DID_NOT_FIND_WHAT_I_WAS_LOOKING_FOR'],
            'likelihood_of_return': 'LIKELY',
            'site_intentions': ['PUT_US_IN_TOUCH_WITH_EXPERTS'],
        },
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_csat_widget(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:csat-widget-submit') + '?url=http://testurl.com'
    response = client.post(url, {'satisfaction': 'SATISFIED', 'user_journey': 'DASHBOARD'})
    assert response.status_code == 302


@pytest.mark.parametrize(
    'form_data',
    (({'feedback_text': 'Some example feedback', 'next': 'http://www.somerefererurl.com'}),),
)
@mock.patch('directory_forms_api_client.actions.SaveOnlyInDatabaseAction')
@pytest.mark.django_db
def test_feedback_submit(mock_save_only_in_database_action, form_data, client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:feedback') + '?next=' + form_data['next']
    response = client.post(
        url,
        form_data,
    )
    assert mock_save_only_in_database_action.call_count == 1
    assert response.status_code == 302


@pytest.mark.django_db
@mock.patch.object(sso_helpers, 'regenerate_verification_code')
@mock.patch.object(sso_helpers, 'send_verification_code_email')
def test_business_eyb_sso_login(mock_send_code, mock_regenerate_code, client, requests_mock):
    mock_regenerate_code.return_value = {'code': '12345', 'user_uidb64': 'aBcDe', 'verification_token': '1ab-123abc'}
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=401)

    response = client.post(
        reverse_lazy('international_online_offer:login'), {'email': 'test@test.com', 'password': 'passwor1234'}
    )

    assert mock_send_code.call_count == 1
    assert mock_regenerate_code.call_count == 1

    assert response.status_code == 200


@pytest.mark.django_db
def test_business_eyb_sso_login_fail(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=200)
    response = client.post(
        reverse_lazy('international_online_offer:login'), {'email': 'test@test.com', 'password': 'passwor1234'}
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_business_eyb_sso_login_success(client, requests_mock):
    requests_mock.post(settings.SSO_PROXY_LOGIN_URL, status_code=302)
    response = client.post(
        reverse_lazy('international_online_offer:login'), {'email': 'test@test.com', 'password': 'passwor1234'}
    )
    assert response.status_code == 302


@pytest.mark.django_db
@mock.patch.object(sso_helpers, 'send_verification_code_email')
def test_business_eyb_sso_signup_success(mock_send_code, client, requests_mock):
    requests_mock.post(
        settings.DIRECTORY_SSO_API_CLIENT_BASE_URL + 'api/v1/user/',
        text='{"uidb64": "133", "verification_token" : "344", "verification_code" : "54322"}',
        status_code=201,
    )
    response = client.post(
        reverse_lazy('international_online_offer:signup'), {'email': 'test@test.com', 'password': 'passwor1234'}
    )
    assert mock_send_code.call_count == 1
    assert response.status_code == 302


@mock.patch.object(sso_api_client.user, 'create_user')
@pytest.mark.django_db
def test_business_eyb_sso_signup_fail(mock_create_user, client):
    mock_create_user.return_value = create_response(status_code=400, json_body={'email': ['Incorrect email']})
    response = client.post(
        reverse_lazy('international_online_offer:signup'), {'email': 'test@test.com', 'password': 'passwor1234'}
    )
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(sso_helpers, 'regenerate_verification_code')
@mock.patch.object(sso_helpers, 'send_verification_code_email')
@mock.patch.object(sso_api_client.user, 'create_user')
def test_business_eyb_sso_signup_regen_code(
    mock_create_user, mock_send_code, mock_regenerate_code, client, requests_mock
):
    mock_create_user.return_value = create_response(status_code=409)
    response = client.post(
        reverse_lazy('international_online_offer:signup'), {'email': 'test@test.com', 'password': 'passwor1234'}
    )
    assert mock_regenerate_code.call_count == 1
    assert mock_send_code.call_count == 1
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch.object(helpers, 'send_welcome_notification')
def test_business_eyb_sso_signup_verify_code_success(mock_send_welcome_notification, client, requests_mock):
    requests_mock.post(
        settings.DIRECTORY_SSO_API_CLIENT_BASE_URL + 'api/v1/verification-code/verify/',
        text='{"uidb64": "133", "token" : "344", "code" : "54322", "email" : "test@test.com"}',
        status_code=201,
    )
    response = client.post(
        reverse_lazy('international_online_offer:signup') + '?uidb64=133&token=344', {'code_confirm': '54322'}
    )
    assert mock_send_welcome_notification.call_count == 1
    assert response.status_code == 302


@pytest.mark.django_db
def test_eyb_signup_partial_complete_signup_redirect(settings, client, user):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:signup')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 302
