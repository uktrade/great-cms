import hvac

from django.conf import settings
from django.core.management.base import BaseCommand

from great_components.janitor.management.commands import helpers


class Command(BaseCommand):

    help = 'Diff the vault of two environments.'

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
            '--wizard',
            action='store_true',
            help='Select the projects and environments from a list.'
        )
        parser.add_argument(
            '--root',
            default=getattr(settings, 'DIRECTORY_COMPONENTS_VAULT_ROOT_PATH', None),
            help='The vault root path your projects are within.'
        )
        parser.add_argument(
            '--project',
            default=getattr(settings, 'DIRECTORY_COMPONENTS_VAULT_PROJECT', None),
            help='The name of the project you want to diff.'
        )
        parser.add_argument(
            '--environment_a',
            required=False,
            help='The first environment to compare (against environment_a).'
        )
        parser.add_argument(
            '--environment_b',
            required=False,
            help='The second environment to compare (against environment_b).'
        )

    def handle(self, *args, **options):
        client = hvac.Client(
            url=f"https://{options['domain']}", token=options['token']
        )
        assert client.is_authenticated()

        if options['wizard']:
            secrets_a = helpers.get_secrets_wizard(client=client, root=options['root'])
            secrets_b = helpers.get_secrets_wizard(client=client, root=options['root'])
        else:
            secrets_a = helpers.get_secrets(
                client=client,
                path=f"{options['root']}/{options['project']}/{options['environment_a']}",
            )
            secrets_b = helpers.get_secrets(
                client=client,
                path=f"{options['root']}/{options['project']}/{options['environment_b']}",
            )
        diff = helpers.diff_dicts(secrets_a, secrets_b)
        self.stdout.write('\n'.join(helpers.colour_diff(diff)))
