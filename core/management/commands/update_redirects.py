import argparse
import csv
from io import StringIO

from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Site


class Command(BaseCommand):
    help = 'Updates Redirects for BGS go-live'

    site_str = 'Great.gov.uk'

    def add_arguments(self, parser):
        parser.add_argument('--site_hostname', type=str, required=True, help='Site hostname (e.g., Great.gov.uk)')
        parser.add_argument(
            '--redirect-file-name', type=str, help='redirect-map.csv', default='redirect-map.csv'
        )
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
        site_hostname = options['site_hostname']
        redirect_file_name = options['redirect_file_name']

        self.site = Site.objects.get(hostname=site_hostname)

        self.stdout.write(self.style.SUCCESS('Updating Redirects'))

        with open(
            settings.ROOT_DIR / f'core/fixtures/{redirect_file_name}',
            'r',
            encoding='utf-8',
        ) as f:
            total_urls_exceed_limit = 0
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                if len(row) < 2:
                    self.stdout(self.style.WARNING(f'Skipping row: {row}'))
                    continue

                old_path = row.get('Current URL').strip()
                redirect_path = row.get('New URL').strip()
                if len(old_path) > 255:
                    self.stdout.write(self.style.WARNING(f'Redirect old_path too long - {old_path}'))
                    total_urls_exceed_limit += 1
                    continue
                if len(redirect_path) > 255:
                    self.stdout.write(self.style.WARNING(f'Redirect redirect_link too long - {redirect_path}'))
                    total_urls_exceed_limit += 1
                    continue
                redirect = Redirect.objects.filter(old_path=old_path, site=self.site).first()
                if redirect:
                    self.update_redirect(redirect, redirect_path)
                else:
                    redirect = self.create_redirect(old_path, redirect_path)
                if redirect and not dry_run:
                    redirect.save()

            self.stdout.write(self.style.SUCCESS(f'total_urls_exceed_limit: {total_urls_exceed_limit}'))
            self.stdout.write(self.style.SUCCESS('Redirect Data Updated'))
