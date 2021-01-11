from unittest import mock

import pytest
from directory_components.janitor.management.commands import helpers


def test_prompt_user_choice(monkeypatch):
    mock_input = mock.Mock(return_value='0')

    monkeypatch.setitem(__builtins__, 'input', mock_input)

    helpers.prompt_user_choice(message='Choose a thing', options=['Option A', 'Option B'])
    assert mock_input.call_count == 1
    assert mock_input.call_args == mock.call('Choose a thing:\n\n[0] Option A\n[1] Option B\n\n')


def test_clean_secrets_default():
    secrets = {
        'SECRET_KEY': '123',
        'PASSWORD': '123',
        'MAGIC_TOKEN': '123',
        'API_KEY': '123',
        'BENIGN': True,
    }
    assert helpers.clean_secrets(secrets) == {
        'SECRET_KEY': '💀💀💀💀💀',
        'PASSWORD': '💀💀💀💀💀',
        'MAGIC_TOKEN': '💀💀💀💀💀',
        'API_KEY': '💀💀💀💀💀',
        'BENIGN': True,
    }


def test_clean_secrets_explicit(settings):
    settings.DIRECTORY_COMPONENTS_VAULT_IGNORE_SETTINGS_REGEX = []

    secrets = {
        'SECRET_KEY': '123',
        'PASSWORD': '123',
        'MAGIC_TOKEN': '123',
        'API_KEY': '123',
        'BENIGN': True,
    }
    assert helpers.clean_secrets(secrets) == secrets


def test_get_secrets():
    mock_client = mock.Mock()
    mock_client.read.return_value = {
        'data': {
            'data': {
                'API_KEY': '123',
                'BENIGN': True,
            }
        }
    }

    result = helpers.get_secrets(client=mock_client, path='/root/foo')

    assert result == {
        'API_KEY': '123',
        'BENIGN': True,
    }
    assert mock_client.read.call_count == 1
    assert mock_client.read.call_args == mock.call(path='/root/foo')


def test_get_secrets_wizard(monkeypatch):
    mock_input = mock.Mock()
    mock_client = mock.Mock()

    monkeypatch.setitem(__builtins__, 'input', mock_input)
    mock_client.read.return_value = {
        'data': {
            'data': {
                'API_KEY': '123',
                'BENIGN': True,
            }
        }
    }
    mock_client.list.side_effect = [
        {'data': {'keys': ['project-one', 'project-two', 'project-three']}},
        {'data': {'keys': ['environment-one', 'environment-two']}},
    ]
    mock_input.side_effect = ['0', '1']

    helpers.get_secrets_wizard(client=mock_client, root='/root/')

    assert mock_input.call_count == 2
    assert mock_input.call_args == mock.call(
        '(/root/project-one) Choose an environment::\n\n[0] environment-one\n[1] environment-two\n\n'
    )


@mock.patch.object(helpers.Vulture, 'get_unused_code')
def test_vulture_filters_non_settings(mock_get_unused_code):
    one = mock.Mock(**{'get_report.return_value': 'conf/settings.py'})
    one.name = 'FOO'
    two = mock.Mock(**{'get_report.return_value': 'conf/settings.py'})
    two.name = 'BAR'
    three = mock.Mock(**{'get_report.return_value': 'views/view.py'})

    mock_get_unused_code.return_value = [one, two, three]

    vulture = helpers.Vulture(verbose=False, ignore_names=[], ignore_decorators=False)
    assert list(vulture.report()) == ['FOO', 'BAR']


def test_get_settings_source_code(settings):
    settings.SETTINGS_MODULE = 'tests.conftest'

    assert helpers.get_settings_source_code(settings)


@pytest.mark.parametrize(
    'value, expected',
    (
        (
            ('SSO_PROXY_LOGOUT_URL', 'SSO_PROXY_LOGOUT_URL'),
            ('DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON', 'DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON'),
            ('ON', None),  # partial match false positive
            ('FOO', None),
            ('foo', None),
            ('Foo', None),
            ('EMAIL_REQUIRED', 'ACCOUNT_EMAIL_REQUIRED'),  # partial match
            ('DUBUG', None),  # django provided
            ('LIBRARY_SECRET_KEY', None),  # partial match that looks like django provided
        )
    ),
)
def test_resolve_setting_name(value, expected):
    settings_keys = [
        'SSO_PROXY_LOGOUT_URL',
        'ACCOUNT_EMAIL_REQUIRED',
        'DIRECTORY_CONSTANTS_URL_SINGLE_SIGN_ON',
    ]
    assert helpers.resolve_setting_name(name=value, settings_keys=settings_keys) == expected


def test_list_vault_paths():
    def stub_list_vault_paths(path):
        keys = {
            '/root/metadata': ['project_a/', 'project_b/'],
            '/root/metadata/project_a/': ['environment_a', 'environment_b'],
            '/root/metadata/project_b/': ['environment_c', 'environment_d'],
        }[path]
        return {'data': {'keys': keys}}

    mock_client = mock.Mock(list=mock.Mock(wraps=stub_list_vault_paths))

    paths = list(helpers.list_vault_paths(client=mock_client, root='/root'))

    assert mock_client.list.call_count == 3
    assert mock_client.list.call_args_list == [
        mock.call(path='/root/metadata'),
        mock.call(path='/root/metadata/project_a/'),
        mock.call(path='/root/metadata/project_b/'),
    ]

    assert paths == [
        '/root/data/project_a/environment_a',
        '/root/data/project_a/environment_b',
        '/root/data/project_b/environment_c',
        '/root/data/project_b/environment_d',
    ]


def tet_import_by_string():
    imported = helpers.import_by_string('directory_components.janitor.management.commands.helpers')
    assert imported is helpers
