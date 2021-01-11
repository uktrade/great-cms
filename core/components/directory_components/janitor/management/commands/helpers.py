import difflib
from pprint import pformat
import importlib
import inspect
import re

from colors import red, green
from vulture import Vulture

from django.core.management.commands.diffsettings import module_to_dict
from django.conf import global_settings, settings


DEFAULT_UNSAFE_SETTINGS = [
    re.compile('.*?PASSWORD.*?'),
    re.compile('.*?SECRET.*?'),
    re.compile('.*?AUTHORIZATION.*?'),
    re.compile('.*?KEY.*?'),
    re.compile('.*?TOKEN.*?'),
    re.compile('.*?DSN.*?'),
]


def list_vault_paths(client, root):
    response = client.list(path=f'{root}/metadata')
    for project in response['data']['keys']:
        response = client.list(path=f'{root}/metadata/{project}')
        for environment in response['data']['keys']:
            yield f'{root}/data/{project}{environment}'


def get_secrets_wizard(client, root):
    response = client.list(path=root)
    project = prompt_user_choice(
        message=f'{root} Choose a projects:',
        options=response['data']['keys'],
    )

    response = client.list(path=f'{root}/{project}')
    environment = prompt_user_choice(
        message=f'({root}{project}) Choose an environment:',
        options=response['data']['keys'],
    )

    return get_secrets(
        client=client,
        path=f'{root}/data{project}{environment}',
    )


def prompt_user_choice(message, options):
    display = '\n'.join([f'{[i]} {option}' for i, option in enumerate(options)])
    index = int(input(f'{message}:\n\n{display}\n\n'))
    return options[index]


def clean_secrets(secrets):
    ignore_settings = getattr(
        settings,
        'DIRECTORY_COMPONENTS_VAULT_IGNORE_SETTINGS_REGEX',
        DEFAULT_UNSAFE_SETTINGS
    )
    secrets = secrets.copy()
    for key in secrets:
        for entry in ignore_settings:
            if entry.match(key):
                secrets[key] = '💀' * 5
                break
    return secrets


def get_secrets(client, path):
    response = client.read(path=path)
    return response['data']['data']


def write_secrets(client, path, secrets):
    client.write(path=path, wrap_ttl=None, data=secrets)


def diff_dicts(dict_a, dict_b):
    return difflib.ndiff(
       pformat(clean_secrets(dict_a)).splitlines(),
       pformat(clean_secrets(dict_b)).splitlines(),
    )


def colour_diff(diff):
    for line in diff:
        if line.startswith('+'):
            yield green(line)
        elif line.startswith('-'):
            yield red(line)
        else:
            yield line


class Vulture(Vulture):

    def __init__(self, *args, **kwargs):
        self.settings_keys = list(module_to_dict(settings._wrapped).keys())
        super().__init__(*args, **kwargs)

    def report(self, min_confidence=0):
        for unused_code in self.get_unused_code(min_confidence=min_confidence):
            report = unused_code.get_report()
            if 'conf/settings.py' in report:
                yield unused_code.name

    def visit_Str(self, node):
        # handle cases like getattr(settings, 'SOME_SETTING')
        name = resolve_setting_name(name=node.s, settings_keys=self.settings_keys)
        if name:
            self.used_names.add(name)
        else:
            return super().visit_Str(node)


def get_settings_source_code(settings):
    # SETTINGS_MODULE is set only when the settings are provided from settings.py otherwise
    # when settings are explicitly set via settings.configure SETTINGS_MODULE is empty
    assert settings.SETTINGS_MODULE
    return inspect.getsource(importlib.import_module(settings.SETTINGS_MODULE))


def resolve_setting_name(name, settings_keys):
    resolved_name = None
    match = next((item for item in settings_keys if item == name), None)

    # prevent matching SECRET_KEY to LIBRARY_SECRET_KEY
    if match:
        if not hasattr(global_settings, match):
            resolved_name = match
    else:
        # handle when USERNAME_REQUIRED is used in code that refers to ACCOUNT_USERNAME_REQUIRED setting
        partial_match = next((item for item in settings_keys if item.endswith(name)), None)
        if partial_match:
            # gets prefix for partial matches e.g, ACCOUNT_
            prefix = partial_match.replace(name, '')
            # avoids KEY being misidentified as LIBRARY_SECRET_KEY
            # or heaven forbid C being misidentified as DIRECTORY_CONSTANTS_URL_GREAT_DOMESTIC
            if prefix.count('_') == 1:
                resolved_name = partial_match
    return resolved_name
