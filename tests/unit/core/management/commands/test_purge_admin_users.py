from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

UserModel = get_user_model()


@mock.patch('core.management.commands.purge_admin_users.input', return_value='n')
def test_purge_admin_users_cancel_operation(mock_input):
    with pytest.raises(SystemExit):
        call_command('purge_admin_users')


@pytest.mark.django_db
@mock.patch('django.contrib.auth.management.commands.createsuperuser.Command')
@mock.patch('core.management.commands.purge_admin_users.input', return_value='y')
def test_purge_admin_users(mock_input, mock_createsuperuser):
    UserModel.objects.create_user('alice', 'alice@example.com', 'password')
    UserModel.objects.create_user('bob', 'bob@example.com', 'password')

    assert UserModel.objects.all().count() == 2

    call_command('purge_admin_users')

    assert mock_createsuperuser.call_count == 1
    assert UserModel.objects.all().count() == 0
