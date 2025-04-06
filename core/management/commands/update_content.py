import argparse
import re
import sys
import types
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from numbers import Number
from uuid import UUID

import sentry_sdk
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.base import ModelState
from wagtail.blocks.field_block import CharBlock, RichTextBlock
from wagtail.blocks.list_block import ListBlock
from wagtail.blocks.stream_block import StreamBlock, StreamValue
from wagtail.blocks.struct_block import StructBlock
from wagtail.embeds.blocks import EmbedValue
from wagtail.models import Site
from wagtail.rich_text import RichText

from core.blocks import (
    CountryGuideIndustryBlock,
    IndividualStatisticBlock,
    PerformanceDashboardDataBlock,
    PullQuoteBlock,
    RouteSectionBlock,
)
from core.models import AltTextImage, GreatMedia, RelatedContentCTA


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

    def string_contains_html(self, value):
        return bool(BeautifulSoup(value, 'html.parser').find())

    def replace_string(self, page_title, field, value):  # noqa C901

        if self.string_contains_html(value):
            return self.replace_richtextbox(page_title, source=value)

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

    def replace_richtextbox_report(self, page_title, source):

        soup = BeautifulSoup(source, 'html.parser')

        for value in self.values_to_skip:
            findall = soup.find_all(text=re.compile(value))
            for txt in findall:
                self.stdout.write(self.style.WARNING(f'SKIPPING page:value {page_title}:{txt}'))

    def replace_richtextbox_text(self, page_title, source):

        updated = False
        soup = BeautifulSoup(source, 'html.parser')

        for value in self.strings_to_replace:
            findall = soup.find_all(text=re.compile(value))
            for link in findall:
                fixed_link = link.replace(value, self.strings_to_replace[value])
                link.replace_with(fixed_link)
                updated = True

        return updated, str(soup)

    def replace_richtextbox_links(self, page_title, source):

        updated = False
        soup = BeautifulSoup(source, 'html.parser')
        a_tags = soup.find_all('a', href=True)
        for tag in a_tags:
            for value in self.strings_to_replace:
                if value in tag['href']:
                    tag['href'] = tag['href'].replace(value, self.strings_to_replace[value])
                    updated = True
        return updated, str(soup)

    def process_string_field(self, page_title, field, value):
        updated, new_value = self.replace_string(page_title, field, value)
        return updated, new_value

    def replace_richtextbox(self, page_title, block=None, source=None):
        block_updated = False
        updated, new_source = self.replace_richtextbox_text(page_title, block.value.source if block else source)
        if updated:
            block_updated = True
        updated, new_source = self.replace_richtextbox_links(page_title, new_source)
        if updated:
            block_updated = True
        self.replace_richtextbox_report(page_title, new_source)
        if updated:
            block_updated = True

        return block_updated, new_source

    def process_richtext_block(self, page_title, block):
        updated, new_source = self.replace_richtextbox(page_title, block=block)
        if updated:
            setattr(block.value, 'source', new_source)
        return updated, block

    def process_stream_block(self, page_title, block):
        block_updated = False

        if isinstance(block, StreamValue):
            updated, new_value = self.process_streamvalue_field(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block, StreamValue.StreamChild):
            updated, val = self.process_streamvalue_field(page_title, block.value)
            if updated:
                block_updated = True
        else:
            self.stdout.write(self.style.WARNING(f'Unhandled Block Type: {type(block)}'))
            sys.exit(-1)

        return block_updated, block

    def process_alttextimage_field(self, page_title, field_name, field_value):
        updated = False
        alt_text = field_value.alt_text
        if alt_text:
            updated, new_alt_text = self.replace_string(page_title, 'alt_text', alt_text)
        return updated, field_value

    def process_greatmedia_field(self, page_title, field_name, field_value):
        block_updated = False
        description = field_value.description
        if description:
            updated, new_description = self.replace_string(page_title, 'description', description)
            if updated:
                block_updated = True
        transcript = field_value.transcript
        if transcript:
            updated, new_transcript = self.replace_string(page_title, 'transcript', transcript)
            if updated:
                block_updated = True
        subtitles_en = field_value.subtitles_en
        if subtitles_en:
            updated, new_subtitles_en = self.replace_string(page_title, 'subtitles_en', subtitles_en)
            if updated:
                block_updated = True
        return block_updated, field_value

    def process_structblock_block(self, page_title, block):  # noqa C901
        block_updated = False
        for field_name, field_value in block.value.items():
            if not field_value:
                continue
            if isinstance(field_value, str):
                updated, new_value = self.process_string_field(page_title, field_name, field_value)
                if updated:
                    block_updated = True
            elif isinstance(field_value, RichText):
                pass
            elif isinstance(field_value, StreamValue):
                updated, new_value = self.process_streamvalue_field(page_title, field_value)
                if updated:
                    block_updated = True
            elif isinstance(field_value, AltTextImage):
                updated, new_value = self.process_alttextimage_field(page_title, field_name, field_value)
                if updated:
                    block_updated = True
            elif isinstance(field_value, GreatMedia):
                updated, new_value = self.process_greatmedia_field(page_title, field_name, field_value)
                if updated:
                    block_updated = True
            elif isinstance(field_value, EmbedValue):
                continue
            else:
                self.stdout.write(self.style.WARNING(f'Unhandled Block Type: {type(field_value)}'))
                sys.exit(-1)
        return block_updated, block

    def process_pullquoteblock_block(self, page_title, block):
        block_updated = False
        updated, new_quote = self.replace_string(page_title, 'quote', block.value['quote'])
        if updated:
            block.value['quote'] = new_quote
            block_updated = True
        updated, new_attribution = self.replace_string(page_title, 'attribution', block.value['attribution'])
        if updated:
            block.value['attribution'] = new_attribution
            block_updated = True
        updated, new_role = self.replace_string(page_title, 'role', block.value['role'])
        if updated:
            block.value['role'] = new_role
            block_updated = True
        updated, new_organisation = self.replace_string(page_title, 'organisation', block.value['organisation'])
        if updated:
            block.value['organisation'] = new_organisation
            block_updated = True
        updated, new_organisation_link = self.replace_string(
            page_title, 'organisation_link', block.value['organisation_link']
        )
        if updated:
            block.value['organisation_link'] = new_organisation_link
            block_updated = True
        return block_updated, block

    def process_routesectionblock_block(self, page_title, block):
        block_updated = False
        updated, new_title = self.replace_string(page_title, 'title', block.value['title'])
        if updated:
            block.value['title'] = new_title
            block_updated = True
        updated, new_body = self.replace_string(page_title, 'body', block.value['body'])
        if updated:
            block.value['body'] = new_body
            block_updated = True
        return block_updated, block

    def process_performancedashboarddatablock_block(self, page_title, block):
        updated = False
        data_description = block.value['data_description']
        updated, new_source = self.replace_richtextbox(page_title, source=data_description.source)
        if updated:
            setattr(block.value['data_description'], 'source', new_source)
        return updated, block

    def process_individualstatisticblock_block(self, page_title, block):
        block_updated = False
        updated, new_smallprint = self.replace_string(page_title, 'smallprint', block.value['smallprint'])
        if updated:
            setattr(block.value['smallprint'], new_smallprint)
            block_updated = True
        updated, new_heading = self.replace_string(page_title, 'heading', block.value['heading'])
        if updated:
            setattr(block.value['heading'], new_heading)
            block_updated = True
        return block_updated, block

    def process_countryguidecasestudyblock_block(self, page_title, block):
        block_updated = False
        updated, new_title = self.replace_string(page_title, 'title', block['title'])
        if updated:
            block['title'] = new_title
            block_updated = True
        updated, new_description = self.replace_string(page_title, 'description', block['description'])
        if updated:
            block['description'] = new_description
            block_updated = True
        updated, new_button_text = self.replace_string(page_title, 'button_text', block['button_text'])
        if updated:
            block['button_text'] = new_button_text
            block_updated = True
        updated, new_button_link = self.replace_string(page_title, 'button_link', block['button_link'])
        if updated:
            block['button_link'] = new_button_link
            block_updated = True
        return block_updated, block

    def process_countryguideindustryblock_block(self, page_title, block):
        block_updated = False
        updated, new_title = self.replace_string(page_title, 'title', block.value['title'])
        if updated:
            block.value['title'] = new_title
            block_updated = True
        updated, new_teaser = self.replace_string(page_title, 'teaser', block.value['teaser'])
        if updated:
            block.value['teaser'] = new_teaser
            block_updated = True
        updated, new_subsections = self.process_stream_block(page_title, block.value['subsections'])
        if updated:
            block.value['subsections'] = new_subsections
            block_updated = True

        updated, new_case_study = self.process_countryguidecasestudyblock_block(page_title, block.value['case_study'])
        if updated:
            block.value['case_study'] = new_case_study
            block_updated = True

        return block_updated, block

    def process_charblock_block(self, page_title, block):
        updated = False
        updated, new_value = self.replace_string(page_title, block.block_type, block.value)
        if updated:
            block.value = new_value
        return updated, block

    def process_listblock_block(self, page_title, block):
        block_updated = False
        for item in block.value:
            if isinstance(item, RelatedContentCTA):
                updated, new_link_text = self.replace_string(page_title, 'link_text', item.link_text)
                if updated:
                    block.value[item].link_text = new_link_text
                    block_updated = True
            else:
                self.stdout.write(self.style.WARNING(f'Unhandled List Item Type: {type(item)}'))
                sys.exit(-1)

        return block_updated, block

    def process_block(self, page_title, block):  # noqa C901

        block_updated = False

        self.stdout.write(
            self.style.SUCCESS(f'Processing Block type:type(value) - {block.block_type}:{type(block.value)}')
        )

        if isinstance(block.block, RichTextBlock):
            updated, new_block = self.process_richtext_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, StreamBlock):
            updated, new_block = self.process_stream_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, PullQuoteBlock):
            updated, new_block = self.process_pullquoteblock_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, RouteSectionBlock):
            updated, new_block = self.process_routesectionblock_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, PerformanceDashboardDataBlock):
            updated, new_block = self.process_performancedashboarddatablock_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, IndividualStatisticBlock):
            updated, new_block = self.process_individualstatisticblock_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, CountryGuideIndustryBlock):
            updated, new_block = self.process_countryguideindustryblock_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, StructBlock):
            self.process_structblock_block(page_title, block)
        elif isinstance(block.block, CharBlock):
            updated, new_block = self.process_charblock_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, ListBlock):
            updated, new_block = self.process_listblock_block(page_title, block)
            if updated:
                block_updated = True
        else:
            self.stdout.write(self.style.WARNING(f'Unhandled Block type: {type(block.block)}'))
            sys.exit(-1)
        return block_updated

    def process_streamvalue_field(self, page_title, value):
        block_updated = False
        for block in value:
            if block.block_type.lower() in (
                'button',
                'image',
                'video',
                'page',
                'image_full_width',
                'task',
                'case_study',
                'table',
            ):
                continue
            updated = self.process_block(page_title, block)
            if updated:
                block_updated = True
        return block_updated, value

    def process_list_field(self, page_title, field, value):
        block_updated = False
        enumerate_list = tuple(enumerate(value))
        for index, item in enumerate_list:
            if isinstance(item, str):
                updated, new_item = self.replace_string(page_title, field, item)
                if updated:
                    value[index] = new_item
                    block_updated = True
            else:
                self.stdout.write(self.style.WARNING(f'Unhandled List Field type: {type(item)}'))
                sys.exit(-1)
        return block_updated, value

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
            updated, new_value = self.process_streamvalue_field(page.title, value)
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
