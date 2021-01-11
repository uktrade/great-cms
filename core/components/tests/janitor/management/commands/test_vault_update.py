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
    patched = mock.patch.object(helpers, 'get_secrets', return_value={'FOO_A': 'foo.uktrade.io', 'PASSWORD': 'foo bar'})
    yield patched.start()
    patched.stop()


@pytest.fixture(autouse=True)
def mock_list_vault_paths():
    patched = mock.patch.object(helpers, 'list_vault_paths', return_value=['foo/bar/baz'])
    yield patched.start()
    patched.stop()


@pytest.fixture(autouse=True)
def mock_write_secrets():
    patched = mock.patch.object(
        helpers,
        'write_secrets',
    )
    yield patched.start()
    patched.stop()


def mutator(secrets, path):
    for key, value in secrets.items():
        secrets[key] = value.replace('uktrade.io', 'uktrade.digital')
    return secrets


@mock.patch('builtins.input', return_value=0)  # index of `Yes'
def test_vault_update(mock_input, mock_get_secrets, mock_write_secrets):
    out = io.StringIO()

    call_command('vault_update', token='secret-token', domain='example.com', mutator=mutator, stdout=out)

    assert red("- {'FOO_A': 'foo.uktrade.io', 'PASSWORD': '💀💀💀💀💀'}") in mock_input.call_args[0][0]
    assert green("+ {'FOO_A': 'foo.uktrade.digital', 'PASSWORD': '💀💀💀💀💀'}") in mock_input.call_args[0][0]
    assert mock_write_secrets.call_args == mock.call(
        client=mock.ANY, path='foo/bar/baz', secrets={'FOO_A': 'foo.uktrade.digital', 'PASSWORD': 'foo bar'}
    )
