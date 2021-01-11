import hvac

from django.conf import settings
from django.core.management.base import BaseCommand

from directory_components.janitor.management.commands import helpers


def import_by_string(full_name):
    module_name, unit_name = full_name.rsplit('.', 1)
    return getattr(__import__(module_name, fromlist=['']), unit_name)


class Command(BaseCommand):

    help = 'Change the vault values based on some mutator function.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--token',
            help='Vault token. Retrieve by clicking "copy token" on Vault UI.'
        )
        parser.add_argument(
            '--domain',
            default=getattr(settings, 'DIRECTORY_COMPONENTS_VAULT_DOMAIN', None),
            help='Vault domain. The domain you uses to access the UI.'
        )
        parser.add_argument(
            '--root',
            default=getattr(settings, 'DIRECTORY_COMPONENTS_VAULT_ROOT_PATH', None),
            help='The vault root path your projects are within.'
        )
        parser.add_argument(
            '--mutator',
            type=import_by_string,
            help='path.to.helper.function.that_mutates(secrets)',
        )

    def handle(self, *args, **options):
        client = hvac.Client(url=f"https://{options['domain']}", token=options['token'])
        assert client.is_authenticated()

        for path in helpers.list_vault_paths(client=client, root=options['root']):
            try:
                secrets = helpers.get_secrets(client=client, path=path)
            except Exception:
                self.stdout.write(f'Error on {path}')
            else:
                new_secrets = options['mutator'](secrets=secrets.copy(), path=path)
                if secrets != new_secrets:
                    diff_dict = helpers.diff_dicts(secrets, new_secrets)
                    diff = '\n'.join(helpers.colour_diff(diff_dict))
                    message = f'{diff}\nUpdate {path}'
                    if helpers.prompt_user_choice(message=message, options=['y', 'n']) == 'y':
                        self.stdout.write(f'Updating {path}')
                        helpers.write_secrets(client=client, path=path, secrets=new_secrets)
