from unittest import mock

import pytest
from django.conf import settings
from django.urls import reverse, reverse_lazy
from rest_framework import status
from rest_framework.response import Response

from directory_sso_api_client import sso_api_client
from international_online_offer.core import (
    helpers,
    hirings,
    intents,
    landing_timeframes,
    regions,
    spends,
)
from international_online_offer.models import (
    CsatFeedback,
    TradeAssociation,
    TriageData,
    UserData,
)
from sso import helpers as sso_helpers
from tests.helpers import create_response


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
        text='{"uidb64": "133", "verification_token" : "344", "verification_code" : "54322", "email": "test@test.com"}',
        status_code=201,
    )
    response = client.post(
        reverse_lazy('international_online_offer:signup'), {'email': 'test@test.com', 'password': 'password1234'}
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


@pytest.mark.django_db
def test_eyb_business_details(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    response = client.get(reverse('international_online_offer:business-details'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_eyb_business_details_next(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    response = client.get(
        reverse('international_online_offer:business-details')
        + '?next='
        + reverse('international_online_offer:change-your-answers')
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_eyb_business_details_next_unhappy(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    response = client.get(reverse('international_online_offer:business-details') + '?next=edit-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_eyb_business_details_initial(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'sector'},
    )
    url = reverse('international_online_offer:business-details')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_eyb_business_details_form_valid_saves_to_db(
    mock_get_dbt_sectors, mock_get_gva_bandings, client, user, settings
):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:business-details')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(
        url,
        {
            'company_name': 'Vault tec',
            'sector_sub': 'SL0003',
            'company_location': 'FR',
            'company_website': 'http://great.gov.uk/',
        },
    )
    assert response.status_code == 302


@mock.patch(
    'directory_api_client.api_client.dataservices.get_dbt_sectors',
    return_value=create_response(
        [
            {
                'id': 1,
                'sector_id': 'SL0003',
                'full_sector_name': 'Advanced engineering : Metallurgical process plant',
                'sector_cluster_name': 'Sustainability and Infrastructure',
                'sector_name': 'Advanced engineering',
                'sub_sector_name': 'Metallurgical process plant',
                'sub_sub_sector_name': '',
            },
        ]
    ),
)
@pytest.mark.django_db
def test_business_details_saved_to_db_gets_sector_labels(
    mock_get_dbt_sectors, mock_get_gva_bandings, client, user, settings
):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:business-details')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(
        url,
        {
            'company_name': 'Vault tec',
            'sector_sub': 'SL0003',
            'company_location': 'FR',
            'company_website': 'http://great.gov.uk/',
        },
    )
    response = client.get(reverse('international_online_offer:business-details'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_intent(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    url = reverse('international_online_offer:intent')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_intent_next(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    response = client.get(
        reverse('international_online_offer:intent')
        + '?next='
        + reverse('international_online_offer:change-your-answers')
    )
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
def test_know_setup_location(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    url = reverse('international_online_offer:know-setup-location')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_know_setup_location_next(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    response = client.get(
        reverse('international_online_offer:know-setup-location')
        + '?next='
        + reverse('international_online_offer:change-your-answers')
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_know_setup_location_initial(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'location_none': False},
    )
    url = reverse('international_online_offer:know-setup-location')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_know_setup_location_form_valid_saves_to_db(
    mock_get_dbt_sectors, mock_get_gva_bandings, client, user, settings
):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:know-setup-location')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'know_setup_location': 'True'})
    assert response.status_code == 302


@pytest.mark.django_db
def test_know_when_want_setup(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    url = reverse('international_online_offer:when-want-setup')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_know_when_want_setup_next(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    response = client.get(
        reverse('international_online_offer:when-want-setup')
        + '?next='
        + reverse('international_online_offer:change-your-answers')
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_know_when_want_setup_initial(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'location_none': False},
    )
    url = reverse('international_online_offer:when-want-setup')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_know_when_want_setup_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:when-want-setup')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'landing_timeframe': landing_timeframes.ONE_TO_TWO_YEARS})
    assert response.status_code == 302


@pytest.mark.django_db
def test_location(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    url = reverse('international_online_offer:location')
    response = client.get(url)
    context = response.context_data
    assert context['region'] is None
    assert context['city'] is None
    assert response.status_code == 200


@pytest.mark.django_db
def test_location_next(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    response = client.get(
        reverse('international_online_offer:location')
        + '?next='
        + reverse('international_online_offer:change-your-answers')
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_location_initial(mock_get_dbt_sectors, client, user, settings):
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
def test_location_form_valid_saves_to_db(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'location': regions.WALES})
    assert response.status_code == 302


@pytest.mark.django_db
def test_location_saved_to_db_gets_labels(mock_get_dbt_sectors, mock_get_gva_bandings, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'location': 'SWANSEA'})
    response = client.get(url)
    context = response.context_data
    assert context['region'] == 'Wales'
    assert context['city'] == 'Swansea'
    assert response.status_code == 200


@pytest.mark.django_db
def test_hiring(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    url = reverse('international_online_offer:hiring')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_hiring_next(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    response = client.get(
        reverse('international_online_offer:hiring')
        + '?next='
        + reverse('international_online_offer:change-your-answers')
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_hiring_initial(mock_get_dbt_sectors, client, user, settings):
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
def test_hiring_form_valid_saves_to_db(mock_get_dbt_sectors, mock_get_gva_bandings, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'hiring': hirings.ONE_TO_FIVE})
    assert response.status_code == 302


@pytest.mark.django_db
def test_spend(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    url = reverse('international_online_offer:spend')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_spend_next(mock_get_dbt_sectors, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    response = client.get(
        reverse('international_online_offer:spend')
        + '?next='
        + reverse('international_online_offer:change-your-answers')
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_spend_initial(mock_get_dbt_sectors, client, user, settings):
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
def test_spend_form_valid_saves_to_db(mock_get_dbt_sectors, mock_get_gva_bandings, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'spend': spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND})
    assert response.status_code == 302


@pytest.mark.django_db
def test_eyb_contact_details(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:contact-details')
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_eyb_contact_details_initial(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    UserData.objects.create(
        hashed_uuid='123',
        full_name='Joe Bloggs',
        role='Director',
        telephone_number='07923456787',
        agree_info_email=False,
    )
    url = reverse('international_online_offer:contact-details')
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
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'Food and drink'},
    )
    TradeAssociation.objects.update_or_create(
        trade_association_id='1244',
        sector_grouping='ANY',
        association_name='TEST',
        website_link='http://test.com',
        sector='Food and drink',
        brief_description='This is a test',
    )
    TradeAssociation.objects.update_or_create(
        trade_association_id='1244',
        sector_grouping='ANY',
        association_name='TEST',
        website_link='http://test.com',
        sector='Technology and smart cities',
        brief_description='This is a test',
    )
    response = client.get(url)
    context = response.context_data
    all_trade_associations = context['all_trade_associations']
    assert len(all_trade_associations) == 1
    assert all_trade_associations[0].sector == 'Food and drink'
    assert response.status_code == 200


@pytest.mark.django_db
def test_feedback(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:feedback')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_csat_feedback(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
    url = reverse('international_online_offer:csat-feedback')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_csat_feedback_with_session_value(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    client.force_login(user)
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


@pytest.mark.django_db
@mock.patch('directory_api_client.api_client.dataservices.get_business_cluster_information_by_dbt_sector')
@mock.patch('international_online_offer.services.get_bci_data')
def test_bci_data(mock_get_bci_data, mock_get_bci_data_api, client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = f"{reverse('international_online_offer:bci')}?area=K03000001"
    user.hashed_uuid = '123'
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'FOOD_AND_DRINK'},
    )
    mock_get_bci_data_api.return_value = create_response(status_code=200)
    mock_get_bci_data.return_value = ({}, {}, {}, 2024, [])
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
@mock.patch('international_online_offer.dnb.api.company_typeahead_search', return_value='[]')
def test_dnb_typeahead_requires_authentication(mock_typeahead_dnp_api, client, user):
    url = reverse('international_online_offer:dnb-typeahead-company-lookup')
    response = client.get(url)
    assert response.status_code == status.HTTP_403_FORBIDDEN

    client.force_login(user)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
@mock.patch('international_online_offer.dnb.api.company_typeahead_search', return_value='[]')
def test_dnb_typeahead_allowed_methods(mock_typeahead_dnp_api, client, user):
    url = reverse('international_online_offer:dnb-typeahead-company-lookup')
    client.force_login(user)

    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK

    response = client.post(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = client.delete(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    response = client.patch(url)
    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
@mock.patch('international_online_offer.dnb.api.company_typeahead_search', return_value='[]')
def test_dnb_typeahead_returns_response_class(mock_typeahead_dnp_api, client, user):
    url = reverse('international_online_offer:dnb-typeahead-company-lookup')
    client.force_login(user)

    response = client.get(url)
    assert type(response) is Response
