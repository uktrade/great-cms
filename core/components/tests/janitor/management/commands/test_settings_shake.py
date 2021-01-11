from unittest import mock
import io
import pytest

from django.core.management import call_command

from directory_components.janitor.management.commands import helpers, settings_shake


@pytest.fixture(autouse=True)
def mock_get_settings_source_code():
    patched = mock.patch.object(
        helpers,
        'get_settings_source_code',
        return_value='EXAMPLE_A = env.bool("EXAMPLE_A")'
    )
    yield patched.start()
    patched.stop()


@pytest.fixture(autouse=True)
def mock_client():
    patched = mock.patch('hvac.Client', mock.Mock(is_authenticated=True))
    yield patched.start()
    patched.stop()


@pytest.fixture(autouse=True)
def mock_get_secrets():
    patched = mock.patch.object(
        helpers,
        'get_secrets',
        return_value={'EXAMPLE_A': True, 'EXAMPLE_B': False}
    )
    yield patched.start()
    patched.stop()


@pytest.fixture(autouse=True)
def mock_vulture():
    mock_vulture = mock.Mock()
    mock_vulture().report.return_value = ['FOO_BAR']
    patched = mock.patch.object(helpers, 'Vulture', mock_vulture)
    yield patched.start()
    patched.stop()


def test_settings_shake_obsolete(settings):
    out = io.StringIO()

    call_command(
        'settings_shake',
        project='example-project',
        environment='example-environment',
        token='secret-token',
        domain='example.com',
        stdout=out
    )
    out.seek(0)
    result = out.read()

    assert 'EXAMPLE_A' not in result
    assert 'EXAMPLE_B' in result


def test_settings_shake_redundant(settings):
    settings.ADMINS = []

    out = io.StringIO()
    call_command(
        'settings_shake',
        project='example-project',
        environment='example-environment',
        token='secret-token',
        domain='example.com',
        stdout=out
    )
    out.seek(0)
    result = out.read()

    assert 'ADMINS' in result


def test_settings_shake_unused(settings):
    out = io.StringIO()
    call_command(
        'settings_shake',
        project='example-project',
        environment='example-environment',
        token='secret-token',
        domain='example.com',
        stdout=out
    )
    out.seek(0)
    result = out.read()

    assert 'FOO_BAR' in result


@mock.patch.object(helpers, 'get_secrets_wizard')
def test_obsolete_wizard(mock_get_secrets_wizard, settings):
    settings.EXAMPLE_A = True

    mock_get_secrets_wizard.return_value = {'EXAMPLE_A': True, 'EXAMPLE_B': False}
    out = io.StringIO()

    call_command(
        'settings_shake',
        wizard=True,
        token='secret-token',
        domain='example.com',
        stdout=out
    )
    out.seek(0)
    result = out.read()

    assert 'EXAMPLE_A' not in result
    assert 'EXAMPLE_B' in result


@mock.patch.object(settings_shake.Command, 'report_obsolete_vault_entries', mock.Mock(return_value=[]))
@mock.patch.object(settings_shake.Command, 'report_unused_settings', mock.Mock(return_value=[]))
@mock.patch.object(settings_shake.Command, 'report_redundant_settings', mock.Mock(return_value=[]))
def test_settings_shake_ok(settings):
    out = io.StringIO()
    call_command(
        'settings_shake',
        project='example-project',
        environment='example-environment',
        token='secret-token',
        domain='example.com',
        stdout=out
    )
    out.seek(0)
    result = out.read()

    assert 'No obsolete vault entries found.' in result
    assert 'No unused settings found.' in result
    assert 'No redundant settings found.' in result
