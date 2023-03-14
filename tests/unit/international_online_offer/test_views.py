import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_ioo_index(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:index')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_ioo_sector(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:sector')
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
<<<<<<< HEAD
def test_triage_spend_session(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:spend')
    client.post(url, {'spend': '2000001-5000000'})
    assert client.session['spend'] == '2000001-5000000'
    assert client.session['spend_other'] is None
=======
def test_ioo_guide(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:guide')
    response = client.get(url)
    assert response.status_code == 200
>>>>>>> a7fbc4d30 (Feature/ioo 428 detailed guide (#2034))


@pytest.mark.django_db
def test_ioo_contact(client, settings):
    settings.FEATURE_INTERNATIONAL_ONLINE_OFFER = True
    url = reverse('international_online_offer:contact')
    response = client.get(url)
    assert response.status_code == 200
