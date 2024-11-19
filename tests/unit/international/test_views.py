from unittest import mock

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_contact(client, settings):
    url = reverse('international:contact')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact_with_param(client, settings):
    url = reverse('international:contact') + '?next=http://anyurl.com'
    response = client.get(url)
    assert response.status_code == 200


@mock.patch('directory_forms_api_client.actions.ZendeskAction')
@pytest.mark.django_db
def test_contact_submit(mock_action_class, client, settings):
    url = reverse('international:contact')
    response = client.post(
        url,
        {
            'full_name': 'Joe Bloggs',
            'email': 'test@test.com',
            'how_we_can_help': 'Help me please.',
        },
    )
    assert response.status_code == 302
