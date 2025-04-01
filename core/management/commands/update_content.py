import argparse
import types
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from numbers import Number
from uuid import UUID

import sentry_sdk
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.base import ModelState
from wagtail.blocks.stream_block import StreamValue
from wagtail.models import Site


class Command(BaseCommand):
    help = 'Update Page Content for BGS site when copied from Prod'

    CALLABLES = types.FunctionType, types.MethodType

    strings_to_replace = {
        'www.great.gov.uk': 'www.hotfix.great.uktrade.digital',
        'great.gov.uk': 'hotfix.great.uktrade.digital',
        'great': 'business growth',
        'Great': 'Business growth',
    }

    def add_arguments(self, parser):
        parser.add_argument(
            '--hostname', type=str, required=True, help='Site hostname (e.g., www.dev.bgs.uktrade.digital)'
        )
        parser.add_argument(
            '--dry_run',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Show summary output only, do not update data',
        )

    def replace_string(self, value):
        updated = False
        for item in self.strings_to_replace:
            if item in value:
                value = value.replace(item, self.strings_to_replace[item])
                updated = True
        return updated, value

    def process_string_field(self, value):
        updated, new_value = self.replace_string(value)
        return updated, new_value

    def process_streamvalue_field(self, page, field, value):
        updated = False
        for block in value:
            pass
        return updated, value

    def process_list_field(self, page, field, value):
        updated = False
        for item in value:
            pass
        return updated, value

    def update_field(self, page, field):

        value = getattr(page, field)

        if (
            not value
            or field == 'specific_class'
            or field == 'specific'
            or isinstance(value, timedelta)
            or isinstance(value, Number)
            or isinstance(value, Decimal)
            or isinstance(value, Fraction)
            or isinstance(value, datetime)
            or isinstance(value, ModelState)
            or isinstance(value, UUID)
        ):
            return field

        if isinstance(value, str):
            updated, new_value = self.process_string_field(value)
        elif isinstance(value, StreamValue):
            updated, new_value = self.process_streamvalue_field(page, field, value)
        elif isinstance(value, list):
            updated, new_value = self.process_list_field(page, field, value)
        else:
            updated = False
            self.stdout.write(self.style.WARNING(f'Unhandled Field type: {type(value)}'))

        if updated:
            setattr(page, field, new_value)
            # page.save()

    def update_page(self, page):

        self.stdout.write(self.style.SUCCESS(f'Processing Page: {page.title}'))

        fields = [key for key, value in page.specific.__dict__.items() if not isinstance(value, self.CALLABLES)]

        for field in fields:
            self.update_field(page.specific, field)

        for child in page.get_children():
            self.update_page(child)

    @transaction.atomic
    def handle(self, *args, **options):  # noqa: C901
        # if settings.APP_ENVIRONMENT.lower() != 'hotfix':
        #     self.stdout.write(self.style.WARNING('Running in env other than hotfix is disabled - exiting'))
        #     return
        hostname = options['hostname']

        try:
            site = Site.objects.get(hostname=hostname)
        except Site.DoesNotExist as e:
            self.stderr.write(self.style.ERROR('Site not found'))
            sentry_sdk.capture_exception(e)
            return

        source_root = site.root_page

        pages_to_update = source_root.get_children()

        for page in pages_to_update:
            self.update_page(page=page)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
