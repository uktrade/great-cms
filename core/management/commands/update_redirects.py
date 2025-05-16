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

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean_slate',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Clear out all Wagtail redirects',
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

    def delete_redirect(self, dry_run):
        self.stdout.write(self.style.SUCCESS('Deleting all redirects from Wagtail'))
        redirects = Redirect.objects.all()
        delete_count = redirects.count()
        if not dry_run:
            redirects.delete()
            self.stdout.write(self.style.SUCCESS(f'Records deleted: {delete_count}'))
        else:
            self.stdout.write(self.style.SUCCESS('Records deleted: None (dry run)'))

    @transaction.atomic
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        clean_slate = options['clean_slate']

        self.bgs_site = Site.objects.get(site_name='Business Growth Service')
        self.site = Site.objects.get(site_name='Great.gov.uk')

        self.stdout.write(self.style.SUCCESS('Starting redirect update'))

        if clean_slate:
            self.delete_redirect(dry_run)

        create_count = 0
        update_count = 0
        with open(
            settings.ROOT_DIR / 'core/fixtures/redirect-map-v2.csv',
            'r',
            encoding='utf-8',
        ) as f:
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                old_path = row.get('CurrentURL').strip()
                redirect_path = row.get('NewURL').strip()
                redirect_path_absolute = f'https://{self.site.hostname}{redirect_path}'

                # Great.go.uk will need absolute_path
                redirect = Redirect.objects.filter(old_path=old_path, site=self.site).first()
                if redirect:
                    self.update_redirect(redirect, redirect_path_absolute)
                    update_count += 1
                else:
                    redirect = self.create_redirect(old_path, redirect_path_absolute)
                    create_count += 1
                if redirect and not dry_run:
                    redirect.save()

                # business.go.uk will need absolute_path
                redirect = Redirect.objects.filter(old_path=old_path, site=self.bgs_site).first()
                if redirect:
                    self.update_redirect(redirect, redirect_path)
                    update_count += 1
                else:
                    redirect = self.create_redirect(old_path, redirect_path)
                    create_count += 1
                if redirect and not dry_run:
                    redirect.save()

            self.stdout.write(self.style.SUCCESS(f'Updated {update_count} records'))
            self.stdout.write(self.style.SUCCESS(f'Created {create_count} records'))
            self.stdout.write(self.style.SUCCESS('Redirect Data Updated'))
