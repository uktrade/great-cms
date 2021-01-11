import io
from unittest import mock

import pytest
from colors import green, red
from directory_components.janitor.management.commands import helpers
from django.core.management import call_command


@pytest.fixture(autouse=True)
def mock_client():
    patched = mock.patch('hvac.Client', mock.Mock(is_authenticated=True))
    yield patched.start()
    patched.stop()


@pytest.fixture(autouse=True)
def mock_get_secrets():
    patched = mock.patch.object(helpers, 'get_secrets', return_value={'EXAMPLE_A': True, 'EXAMPLE_B': False})
    yield patched.start()
    patched.stop()


@pytest.mark.parametrize('command', ['vault_diff', 'environment_diff'])
def test_vault_diff(command, mock_get_secrets):
    mock_get_secrets.side_effect = [
        {'FOO': True, 'BAZ': True},
        {'BAR': False, 'BOX': False},
    ]
    out = io.StringIO()

    call_command(
        command,
        project='example-project',
        environment_a='example-environment-a',
        environment_b='example-environment-a',
        token='secret-token',
        domain='example.com',
        stdout=out,
    )
    out.seek(0)
    result = out.read()

    assert red("- {'BAZ': True, 'FOO': True}") in result
    assert green("+ {'BAR': False, 'BOX': False}") in result


@pytest.mark.parametrize('command', ['vault_diff', 'environment_diff'])
@mock.patch.object(helpers, 'get_secrets_wizard')
def test_wizard(mock_get_secrets_wizard, command):
    mock_get_secrets_wizard.side_effect = [
        {'FOO': True, 'BAZ': True},
        {'BAR': False, 'BOX': False},
    ]
    out = io.StringIO()

    call_command(command, token='secret-token', domain='example.com', wizard=True, stdout=out)
    out.seek(0)
    result = out.read()

    assert red("- {'BAZ': True, 'FOO': True}") in result
    assert green("+ {'BAR': False, 'BOX': False}") in result
