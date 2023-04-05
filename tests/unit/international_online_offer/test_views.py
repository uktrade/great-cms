import pytest
from django.urls import reverse

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
def test_triage_sector_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:sector')
    client.post(url, {'sector': 'Food and Drink'})
    assert client.session['sector'] == 'Food and Drink'


@pytest.mark.django_db
def test_ioo_intent(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:intent')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_intent_initial(client, user, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    TriageData.objects.update_or_create(
        hashed_uuid='123',
        defaults={'sector': 'sector'},
    )
    url = reverse('international_online_offer:intent')
    user.hashed_uuid = '123'
    client.force_login(user)
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_triage_intent_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:intent')
    client.post(url, {'intent': ['Set up new premises']})
    assert client.session['intent'] == ['Set up new premises']
    assert client.session['intent_other'] == ''


@pytest.mark.django_db
def test_ioo_location(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    response = client.get(url)
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
def test_triage_location_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:location')
    client.post(url, {'location': 'Wales'})
    assert client.session['location'] == 'Wales'
    assert client.session['location_none'] is False


@pytest.mark.django_db
def test_ioo_hiring(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    response = client.get(url)
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
def test_triage_hiring_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:hiring')
    client.post(url, {'hiring': '11-50'})
    assert client.session['hiring'] == '11-50'


@pytest.mark.django_db
def test_ioo_spend(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    response = client.get(url)
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
def test_triage_spend_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    client.post(url, {'spend': '2000001-5000000'})
    assert client.session['spend'] == '2000001-5000000'
    assert client.session['spend_other'] is None


@pytest.mark.django_db
def test_ioo_contact(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:contact')
    response = client.get(url)
    assert response.status_code == 200
