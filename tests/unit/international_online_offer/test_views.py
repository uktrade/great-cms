import pytest
from django.urls import reverse

from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import hirings, intents, regions, spends
from international_online_offer.models import TriageData


@pytest.mark.django_db
def test_ioo_index(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:index')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_sector(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:sector'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_sector_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:sector') + '?next=edit-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_sector_initial(client, user, settings):
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
def test_ioo_sector_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:sector')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'sector': directory_constants_sectors.FOOD_AND_DRINK})
    assert response.status_code == 302


@pytest.mark.django_db
def test_ioo_sector_form_valid_saves_to_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:sector')
    response = client.post(url, {'sector': directory_constants_sectors.FOOD_AND_DRINK})
    assert response.status_code == 302


@pytest.mark.django_db
def test_triage_sector_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:sector')
    client.post(url, {'sector': directory_constants_sectors.FOOD_AND_DRINK})
    assert client.session['sector'] == directory_constants_sectors.FOOD_AND_DRINK


@pytest.mark.django_db
def test_ioo_intent(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:intent')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_intent_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:intent') + '?next=edit-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_intent_initial(client, user, settings):
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
def test_ioo_intent_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:intent')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'intent': intents.SET_UP_NEW_PREMISES, 'intent_other': ''})
    assert response.status_code == 302


@pytest.mark.django_db
def test_ioo_intent_form_valid_saves_to_session(client, settings):
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
def test_ioo_location(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_location_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:location') + '?next=edit-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_location_initial(client, user, settings):
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
def test_ioo_location_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'location': regions.WALES})
    assert response.status_code == 302


@pytest.mark.django_db
def test_ioo_location_form_valid_saves_to_session(client, settings):
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
def test_ioo_hiring(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_hiring_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:hiring') + '?next=edit-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_hiring_initial(client, user, settings):
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
def test_ioo_hiring_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'hiring': hirings.ONE_TO_TEN})
    assert response.status_code == 302


@pytest.mark.django_db
def test_ioo_hiring_form_valid_saves_to_session(client, settings):
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
def test_ioo_spend(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_spend_next(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    response = client.get(reverse('international_online_offer:spend') + '?next=edit-your-answers')
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_spend_initial(client, user, settings):
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
def test_ioo_spend_form_valid_saves_to_db(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.post(url, {'spend': spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND})
    assert response.status_code == 302


@pytest.mark.django_db
def test_ioo_spend_form_valid_saves_to_session(client, settings):
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
    assert client.session['spend_other'] is None


@pytest.mark.django_db
def test_ioo_contact(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:contact')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_edit_your_answers(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:edit-your-answers')
    response = client.get(url)
    assert response.status_code == 200
