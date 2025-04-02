import argparse
import types
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from numbers import Number
import sys
from uuid import UUID

import sentry_sdk
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.base import ModelState
from wagtail.blocks.stream_block import StreamValue
from wagtail.models import Site
from wagtail.blocks.field_block import RichTextBlock
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.blocks.stream_block import StreamBlock
from wagtail.blocks.struct_block import StructBlock
from wagtail.blocks.field_block import CharBlock
from  wagtail.blocks.list_block import ListBlock

from core.blocks import CaseStudyStaticBlock, CountryGuideIndustryBlock, IndividualStatisticBlock, PullQuoteBlock, RouteSectionBlock, PerformanceDashboardDataBlock


class Command(BaseCommand):
    help = 'Update Page Content for BGS site when copied from Prod'

    CALLABLES = types.FunctionType, types.MethodType

    strings_to_replace = {
        'www.great.gov.uk': 'www.hotfix.great.uktrade.digital',
        'great.gov.uk': 'hotfix.great.uktrade.digital',
    }

    fields_to_report = (
        'url_path',
        'slug',
    )

    values_to_skip = (
        'Great',
        'great',
    )

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

    def replace_string(self, page_title, field, value):
        updated = True
        for item in self.fields_to_report:
            if item == field:
                self.stdout.write(self.style.WARNING(f'SKIPPING page:field:value {page_title}:{field}:{value}'))
                updated = False

        if not updated:
            return updated, value
        
        updated = False

        for item in self.strings_to_replace:
            if item in value:
                value = value.replace(item, self.strings_to_replace[item])
                updated = True

        if not updated:     
            for item in self.values_to_skip:
                if item in value:
                    self.stdout.write(self.style.WARNING(f'SKIPPING page:field:value {page_title}:{field}:{value}'))
                    updated = False
        
        return updated, value


    def process_string_field(self, page_title, field, value):
        updated, new_value = self.replace_string(page_title, field, value)
        return updated, new_value

    def process_richtext_block(self, block):
        pass

    def process_table_block(self, block):
        pass

    def process_stream_block(self, block):
        pass

    def process_pullquoteblock_block(self, block):
        pass

    def process_routesectionblock_block(self, block):
        pass

    def process_performancedashboarddatablock_block(self, block):
        pass

    def process_individualstatisticblock_block(self, block):
        pass

    def process_countryguideindustryblock_block(self, block):
        pass

    def process_structblock_block(self, block):
        pass

    def process_charblock_block(self, block):
        pass

    def process_casestudystaticblock_block(self, block):
        pass

    def process_listblock_block(self, block):
        pass

    def process_pagechooserblock_block(self, block):
        pass

    def process_block(self, block):
        
        self.stdout.write(self.style.SUCCESS(f'Processing Block type:type(value) - {block.block_type}:{type(block.value)}'))

        if isinstance(block.block, RichTextBlock):
            self.process_richtext_block(block)
        elif isinstance(block.block, TableBlock):
            self.process_table_block(block)
        elif isinstance(block.block, StreamBlock):
            self.process_stream_block(block)
        elif isinstance(block.block, PullQuoteBlock):
            self.process_pullquoteblock_block(block)
        elif isinstance(block.block, RouteSectionBlock):
            self.process_routesectionblock_block(block)
        elif isinstance(block.block, PerformanceDashboardDataBlock):
            self.process_performancedashboarddatablock_block(block)
        elif isinstance(block.block, IndividualStatisticBlock):
            self.process_individualstatisticblock_block(block)
        elif isinstance(block.block, CountryGuideIndustryBlock):
            self.process_countryguideindustryblock_block(block)
        elif isinstance(block.block, StructBlock):
            self.process_structblock_block(block)
        elif isinstance(block.block, CharBlock):
            self.process_charblock_block(block)
        elif isinstance(block.block, CaseStudyStaticBlock):
            self.process_casestudystaticblock_block(block)
        elif isinstance(block.block, ListBlock):
            self.process_listblock_block(block)
        else:
            self.stdout.write(self.style.WARNING(f'Unhandled Block type: {type(block.block)}'))
            sys.exit(-1)

    def process_streamvalue_field(self, page_title, field, value):
        updated = False
        for block in value:
            if block.block_type.lower() in ('button', 'image', 'video', 'page', 'image_full_width', 'task',):
                continue
            self.process_block(block)
        return updated, value

    def process_list_field(self, page_title, field, value):
        updated = False
        enumerate_list = tuple(enumerate(value))
        for index, item in enumerate_list:
            if isinstance(item, str):
                updated, new_item = self.replace_string(page_title, field, item)
                if updated:
                    value[index] = new_item
            else:
                self.stdout.write(self.style.WARNING(f'Unhandled List Field type: {type(item)}'))
                sys.exit(-1)
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
            updated, new_value = self.process_string_field(page.title, field, value)
        elif isinstance(value, StreamValue):
            updated, new_value = self.process_streamvalue_field(page.title, field, value)
        elif isinstance(value, list):
            updated, new_value = self.process_list_field(page.title, field, value)
        else:
            updated = False
            self.stdout.write(self.style.WARNING(f'Unhandled Field type: {type(value)}'))
            sys.exit(-1)

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
