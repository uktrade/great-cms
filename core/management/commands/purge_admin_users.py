import sys

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand, call_command


class Command(BaseCommand):
    help = 'Purge admin users'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()

    def handle(self, *args, **options):
        proceed = input('This operation will purge the users table. Are you sure? [y/N]: ') or 'n'
        if proceed[0].lower() == 'y':
            self.UserModel.objects.all().delete()
        else:
            self.stderr.write('Operation cancelled.')
            sys.exit(1)

        create_superuser = input('Create superuser? [y/N]: ') or 'n'

        if create_superuser[0].lower() == 'y':
            call_command('createsuperuser')

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
