import argparse
import csv
from io import StringIO

from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction
from wagtail.contrib.redirects.models import Redirect


class Command(BaseCommand):
    help = 'Updates Redirects for BGS go-live'

    site = 'Great.gov.uk'

    def add_arguments(self, parser):
        parser.add_argument('--site', type=str, required=True, help='Site (e.g., Great.gov.uk)')
        parser.add_argument(
            '--dry_run',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Show summary output only, do not update data',
        )

    def update_redirect(self, redirect, redirect_path):
        redirect.redirect_link = redirect_path

    def create_redirect(self, old_path, redirect_path):
        redirect = Redirect.objects.create(
            old_path=old_path, is_permanent=True, redirect_link=redirect_path, site=self.site
        )
        return redirect

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        self.site = options['site']

        self.stdout.write(self.style.SUCCESS('Updating Redirects'))

        with open(
            settings.ROOT_DIR / 'core/fixtures/redirect-map.csv',
            'r',
            encoding='utf-8',
        ) as f:
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                old_path = row.get('CurrentURL')
                redirect_path = row.get('NewURL')
                redirect = Redirect.objects.filter(old_path=old_path, site=self.site).first()
                if redirect:
                    self.update_redirect(redirect, redirect_path)
                else:
                    redirect = self.create_redirect(old_path, redirect_path)
                if redirect and not dry_run:
                    redirect.save()

            self.stdout.write(self.style.SUCCESS('Redirect Data Updated'))
