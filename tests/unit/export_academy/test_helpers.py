from unittest import mock

import pytest
from django.contrib.auth.models import AnonymousUser

from export_academy.helpers import is_export_academy_registered, notify_registration
from tests.helpers import create_response
from tests.unit.export_academy import factories


@pytest.mark.django_db
def test_is_export_academy_unregistered():
    user = AnonymousUser()

    assert is_export_academy_registered(user) is False


@pytest.mark.django_db
def test_is_export_academy_registered(user):
    factories.RegistrationFactory(email=user.email)

    assert is_export_academy_registered(user) is True


@mock.patch('directory_forms_api_client.actions.GovNotifyEmailAction')
@pytest.mark.django_db
def test_notify_registration(mock_notify_action):
    mock_notify_action().save.return_value = create_response(status_code=201)

    notify_registration(
        email_data={'one': 1, 'two': 2},
        form_url='/',
        email_address='mail@example.com',
    )

    assert mock_notify_action.call_count == 2
    assert mock_notify_action().save.call_count == 1
    assert mock_notify_action().save.call_args == mock.call({'one': 1, 'two': 2})
