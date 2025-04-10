import argparse
import re
import sys
import types
from datetime import datetime, timedelta
from decimal import Decimal
from fractions import Fraction
from inspect import currentframe, getframeinfo
from numbers import Number
from uuid import UUID

import sentry_sdk
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.base import ModelState
from wagtail.blocks.field_block import CharBlock, RichTextBlock
from wagtail.blocks.list_block import ListBlock
from wagtail.blocks.stream_block import StreamBlock, StreamValue
from wagtail.blocks.struct_block import StructBlock, StructValue
from wagtail.embeds.blocks import EmbedValue
from wagtail.models import Site
from wagtail.rich_text import RichText
from wagtail.snippets.blocks import SnippetChooserBlock

from core.blocks import (
    ArticleListingLinkBlock,
    CountryGuideIndustryBlock,
    DataTableBlock,
    IndividualStatisticBlock,
    LinkStructValue,
    PerformanceDashboardDataBlock,
    PullQuoteBlock,
    RouteSectionBlock,
    SupportTopicCardBlock,
)
from core.models import UKEACTA, AltTextImage, GreatMedia, RelatedContentCTA


class Command(BaseCommand):
    help = 'Update Page Content for BGS site when copied from Prod'

    CALLABLES = types.FunctionType, types.MethodType

    strings_to_replace = {
        'www.great.gov.uk': 'www.hotfix.great.uktrade.digital',
        'great.gov.uk': 'hotfix.great.uktrade.digital',
        'Great.gov.uk': 'hotfix.great.uktrade.digital',
        'great.dev.uktrade.digital': 'hotfix.great.uktrade.digital',
        'great.uat.uktrade.digital': 'hotfix.great.uktrade.digital',
        'https://great.dev.uktrade.digital': 'https://www.hotfix.great.uktrade.digital',
        'https://great.uat.uktrade.digital': 'https://www.hotfix.great.uktrade.digital',
    }

    values_to_report = (
        'great',
        'Great',
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

    def report_page_needs_updating(self, page_title, field_name, field_value):
        self.stdout.write(self.style.WARNING(f'FIELD NEEDS UPDATING - <page>:<field_name> - {page_title}:{field_name}'))

    def string_contains_html(self, value):
        return bool(BeautifulSoup(value, 'html.parser').find())

    def replace_string(self, page_title, field, original_value, dry_run=False):  # noqa C901

        updated = False
        value = original_value

        if self.string_contains_html(original_value):
            updated, new_source = self.replace_richtextbox(page_title, original_value)
            return updated, new_source

        for item in self.strings_to_replace:
            if item in original_value:
                value = original_value.replace(item, self.strings_to_replace[item])
                updated = True

        if any(item in original_value for item in self.values_to_report) and dry_run:
            self.stdout.write(self.style.WARNING(f'SKIPPING page:field:value {page_title}:{field}:{original_value}'))

        if updated:
            self.report_page_needs_updating(page_title, field, original_value)

        return updated, value

    def replace_richtextbox_text(self, page_title, source):

        updated = False
        soup = BeautifulSoup(source, 'html.parser')

        for value in self.strings_to_replace:
            findall = soup.find_all(text=re.compile(value))
            for text in findall:
                self.report_page_needs_updating(page_title, 'text', source)
                fixed_link = text.replace(value, self.strings_to_replace[value])
                text.replace_with(fixed_link)
                updated = True

        return updated, str(soup)

    def replace_richtextbox_links(self, page_title, source):
        updated = False
        soup = BeautifulSoup(source, 'html.parser')
        a_tags = soup.find_all('a', href=True)
        for tag in a_tags:
            for value in self.strings_to_replace:
                if value in tag['href']:
                    self.report_page_needs_updating(page_title, 'link', source)
                    tag['href'] = tag['href'].replace(value, self.strings_to_replace[value])
                    updated = True
        return updated, str(soup)

    def process_string_field(self, page_title, field, value, dry_run):
        updated, new_value = self.replace_string(page_title, field, value, dry_run)
        return updated, new_value

    def replace_richtextbox(self, page_title, original_source):
        block_updated = False
        source = original_source
        updated, source = self.replace_richtextbox_text(page_title, source)
        if updated:
            block_updated = True
        updated, source = self.replace_richtextbox_links(page_title, source)
        if updated:
            block_updated = True

        return block_updated, original_source

    def process_richtext_block(self, page_title, source):
        updated, new_source = self.replace_richtextbox(page_title, source)
        return updated, new_source

    def process_stream_block(self, page_title, block, dry_run):
        block_updated = False

        new_block = block
        if isinstance(block, StreamValue):
            updated, new_block = self.process_streamvalue_field(page_title, block, dry_run)
            if updated:
                self.report_page_needs_updating(page_title, block.block_type, block.value)
                block_updated = True
        elif isinstance(block, StreamValue.StreamChild):
            updated, new_block = self.process_streamchild_field(page_title, block, dry_run)
            if updated:
                self.report_page_needs_updating(page_title, block.block_type, block.value)
                block_updated = True
        else:
            frameinfo = getframeinfo(currentframe())
            self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
            self.stdout.write(self.style.WARNING(f'Unhandled Block Type: {type(block)}'))
            sys.exit(-1)

        return block_updated, new_block

    def process_alttextimage_field(self, page_title, field_name, field_value):
        updated = False
        alt_text = field_value.alt_text
        if alt_text:
            updated, new_alt_text = self.replace_string(page_title, 'alt_text', alt_text)
            if updated:
                field_value.alt_text = new_alt_text

        return updated, field_value

    def process_greatmedia_field(self, page_title, block):  # noqa C901

        block_updated = False

        if block.description:
            updated, new_value = self.replace_string(page_title, 'description', block.description)
            if updated:
                block.description = new_value
                block_updated = True

        if block.transcript:
            updated, new_value = self.replace_string(page_title, 'transcript', block.transcript)
            if updated:
                block.transcript = new_value
                block_updated = True

        if block.subtitles_en:
            updated, new_value = self.replace_string(page_title, 'subtitles_en', block.subtitles_en)
            if updated:
                block.subtitles_en = new_value
                block_updated = True

        return block_updated, block

    def process_structvalue_block(self, page_title, field_name, block, dry_run):  # noqa C901
        block_updated = False
        for name, value in block.items():
            if value:
                if isinstance(value, str):
                    updated, new_value = self.process_string_field(page_title, field_name, value, dry_run)
                    if updated:
                        self.report_page_needs_updating(page_title, field_name, value)
                        setattr(block, name, new_value)
                        block_updated = True
                elif isinstance(value, LinkStructValue):
                    for ln, lv in value.items():
                        if lv:
                            updated, new_value = self.process_string_field(page_title, field_name, lv, dry_run)
                            if updated:
                                block[name][ln] = new_value
                                self.report_page_needs_updating(page_title, field_name, lv)
                                block_updated = True
                elif isinstance(value, bool):
                    continue
                else:
                    frameinfo = getframeinfo(currentframe())
                    self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                    self.stdout.write(self.style.WARNING(f'Unhandled Block Type: {type(block)}'))
                    sys.exit(-1)

        return block_updated, block

    def process_structblock_block(self, page_title, block, dry_run):  # noqa C901
        block_updated = False
        for field_name, field_value in block.value.items():
            if not field_value:
                continue
            if field_name in ('link_page',):
                continue
            if isinstance(field_value, str):
                updated, new_value = self.process_string_field(page_title, field_name, field_value, dry_run)
                if updated:
                    self.report_page_needs_updating(page_title, field_name, field_value)
                    block.value[field_name] = new_value
                    block_updated = True
            elif isinstance(field_value, RichText):
                updated, new_source = self.replace_richtextbox(page_title, field_value.source)
                if updated:
                    field_value.source = new_source
                    block.value[field_name] = field_value
                    self.report_page_needs_updating(page_title, field_name, field_value)
                    block_updated = True
            elif isinstance(field_value, StreamValue):
                updated, new_value = self.process_streamvalue_field(page_title, field_value, dry_run)
                if updated:
                    block.value[field_name] = new_value
                    self.report_page_needs_updating(page_title, field_name, field_value)
                    block_updated = True
            elif isinstance(field_value, AltTextImage):
                updated, new_value = self.process_alttextimage_field(page_title, field_name, field_value)
                if updated:
                    block.value[field_name] = new_value
                    self.report_page_needs_updating(page_title, field_name, field_value)
                    block_updated = True
            elif isinstance(field_value, GreatMedia):
                updated, new_value = self.process_greatmedia_field(page_title, field_value)
                if updated:
                    block.value[field_name] = new_value
                    self.report_page_needs_updating(page_title, field_name, field_value)
                    block_updated = True
            elif isinstance(field_value, EmbedValue):
                continue
            elif isinstance(field_value, StructValue):
                updated, new_value = self.process_structvalue_block(page_title, field_name, field_value, dry_run)
                if updated:
                    block.value[field_name] = new_value
                    self.report_page_needs_updating(page_title, field_name, field_value)
                    block_updated = True
            else:
                frameinfo = getframeinfo(currentframe())
                self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                self.stdout.write(self.style.WARNING(f'Unhandled Block Type: {type(field_value)}'))
                sys.exit(-1)
        return block_updated, block

    def create_original_vales(self, items):
        original = {}
        for field_name, field_value in items:
            original[field_name] = field_value
        return original

    def process_pullquoteblock_block(self, page_title, block):
        block_updated = False
        original_values = self.create_original_vales(block.value.items())
        for field_name, field_value in block.value.items():
            if not field_value:
                continue
            updated, new_value = self.replace_string(page_title, field_name, field_value)
            if updated:
                original_values[field_name] = new_value
                block_updated = True

        if block_updated:
            block.value = original_values

        return block_updated, block

    def process_routesectionblock_block(self, page_title, block):
        block_updated = False
        original_values = self.create_original_vales(block.value.items())
        for field_name, field_value in block.value.items():
            if not field_value:
                continue
            if field_name in (
                'route_type',
                'image',
                'button',
            ):
                continue
            updated, new_value = self.replace_string(page_title, field_name, field_value)
            if updated:
                original_values[field_name] = new_value
                block_updated = True

        if block_updated:
            block.value = original_values

        return block_updated, block

    def process_performancedashboarddatablock_block(self, page_title, block):
        block_updated = False
        original_values = self.create_original_vales(block.value.items())
        for field_name, field_value in block.value.items():
            if not field_value:
                continue
            if field_name in (
                'data_title',
                'data_period',
                'data_value',
            ):
                continue
            updated, new_value = self.replace_richtextbox(page_title, field_value.source)
            if updated:
                original_values[field_name].source = new_value
                block_updated = True

        if block_updated:
            block.value = original_values

        return block_updated, block

    def process_individualstatisticblock_block(self, page_title, block):
        block_updated = False
        original_values = self.create_original_vales(block.value.items())
        for field_name, field_value in block.value.items():
            if not field_value:
                continue
            updated, new_value = self.replace_string(page_title, field_name, field_value)
            if updated:
                original_values[field_name] = new_value
                block_updated = True

        if block_updated:
            block.value = original_values

        return block_updated, block

    def process_countryguidecasestudyblock_block(self, page_title, block, dry_run):
        block_updated = False
        original_values = self.create_original_vales(block.items())
        for field_name, field_value in block.items():
            if not field_value:
                continue

            updated, new_value = self.replace_string(page_title, field_name, field_value, dry_run)
            if updated:
                original_values[field_name] = new_value
                block_updated = True

        if block_updated:
            block.value = original_values

        return block_updated, block

    def process_countryguideindustryblock_block(self, page_title, block, dry_run):  # noqa C901
        block_updated = False

        original_values = self.create_original_vales(block.value.items())
        for field_name, field_value in block.value.items():
            if not field_value:
                continue
            if field_name in ('icon',):
                continue
            if field_name in ('subsections',):
                updated, new_value = self.process_stream_block(page_title, field_value, dry_run)
                if updated:
                    self.report_page_needs_updating(page_title, field_name, field_value)
                    original_values[field_name] = new_value
                    block_updated = True
            elif field_name in ('case_study'):
                updated, new_value = self.process_countryguidecasestudyblock_block(
                    page_title, field_value, dry_run
                )  # noqa C901
                if updated:
                    original_values[field_name] = new_value
                    self.report_page_needs_updating(page_title, field_name, field_value)
                    block_updated = True
            elif field_name in ('statistics',):
                updated, new_value = self.process_stream_block(page_title, field_value, dry_run)
                if updated:
                    original_values[field_name] = new_value
                    self.report_page_needs_updating(page_title, field_name, field_value)
                    block_updated = True
            else:
                updated, new_value = self.replace_string(page_title, field_name, field_value)
                if updated:
                    original_values[field_name] = new_value
                    block_updated = True

        if block_updated:
            block.value = original_values

        return block_updated, block

    def process_charblock_block(self, page_title, block):
        updated = False
        updated, new_value = self.replace_string(page_title, block.block_type, block.value)
        if updated:
            block.value = new_value
        return updated, block

    def process_articlelistinglinkblock_block(self, page_title, block):
        block_updated = False
        original_values = self.create_original_vales(block.value.items())
        for field_name, field_value in block.value.items():
            if not field_value:
                continue
            if field_name in ('link_page',):
                continue
            updated, new_value = self.replace_string(page_title, field_name, field_value)
            if updated:
                original_values[field_name] = new_value
                block_updated = True

        if block_updated:
            block.value = original_values

        return block_updated, block

    def process_datatableblock_block(self, page_title, block, dry_run):
        block_updated = False
        data = block.value['data']
        row_cnt = 0
        for row in data:
            cell_cnt = 0
            for cell in row:
                if cell:
                    if isinstance(cell, str):
                        updated, new_value = self.process_string_field(page_title, 'NOTAPPLICABLE', cell, dry_run)
                        if updated:
                            block.value['data'][row_cnt][cell_cnt] = new_value
                            self.report_page_needs_updating(page_title, row, cell)
                            block_updated = True
                    else:
                        frameinfo = getframeinfo(currentframe())
                        self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                        self.stdout.write(self.style.WARNING(f'Unhandled Data Block Cell Type: {type(cell)}'))
                        sys.exit(-1)
                cell_cnt += 1
            row_cnt += 1

        return block_updated, block

    def process_listblock_block(self, page_title, block, dry_run):
        block_updated = False
        cnt = 0
        for item in block.value:
            if item:
                if isinstance(item, RelatedContentCTA):
                    updated, new_link_text = self.replace_string(page_title, 'link_text', item.link_text)
                    if updated:
                        block.value[cnt].link_text = new_link_text
                        block_updated = True
                    updated, new_link = self.process_streamvalue_field(page_title, item.link, dry_run)
                    if updated:
                        block.value[cnt].link = new_link
                        block_updated = True
                elif isinstance(item, UKEACTA):
                    continue
                else:
                    frameinfo = getframeinfo(currentframe())
                    self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                    self.stdout.write(self.style.WARNING(f'Unhandled List Item Type: {type(item)}'))
                    sys.exit(-1)
            cnt += 1

        return block_updated, block

    def process_supporttopiccardblock_block(self, page_title, block):
        block_updated = False
        original_values = self.create_original_vales(block.value.items())
        for field_name, field_value in block.value.items():
            if not field_value:
                continue
            updated, new_value = self.replace_string(page_title, field_name, field_value)
            if updated:
                original_values[field_name] = new_value
                block_updated = True

        if block_updated:
            block.value = original_values

        return block_updated, block

    def process_block(self, page_title, block, dry_run):  # noqa C901

        block_updated = False

        new_block = block

        if block.block_type == 'content_module':
            return False, block

        if isinstance(block.block, RichTextBlock):
            # updated, new_source = self.process_richtext_block(page_title, block.value.source)
            # if updated:
            #     block.value.source = new_source
            #     block_updated = True
            pass
        elif isinstance(block.block, StreamBlock):
            updated, new_block = self.process_stream_block(page_title, block, dry_run)
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
            updated, new_block = self.process_countryguideindustryblock_block(page_title, block, dry_run)
            if updated:
                block_updated = True

        elif isinstance(block.block, ArticleListingLinkBlock):
            updated, new_block = self.process_articlelistinglinkblock_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, CharBlock):
            updated, new_block = self.process_charblock_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, ListBlock):
            updated, new_block = self.process_listblock_block(page_title, block, dry_run)
            if updated:
                block_updated = True
        elif isinstance(block.block, DataTableBlock):
            updated, new_block = self.process_datatableblock_block(page_title, block, dry_run)
            if updated:
                block_updated = True
        elif isinstance(block.block, SupportTopicCardBlock):
            updated, new_block = self.process_supporttopiccardblock_block(page_title, block)
            if updated:
                block_updated = True
        elif isinstance(block.block, StructBlock):
            updated, new_block = self.process_structblock_block(page_title, block, dry_run)
            if updated:
                block_updated = True
        elif isinstance(block.block, SnippetChooserBlock):
            pass
        else:
            frameinfo = getframeinfo(currentframe())
            self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
            self.stdout.write(self.style.WARNING(f'Unhandled Block type: {type(block.block)}'))
            sys.exit(-1)
        return block_updated, new_block

    def process_streamvalue_field(self, page_title, value, dry_run):
        field_updated = False
        cnt = 0
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
                cnt += 1
                continue
            updated, new_block = self.process_block(page_title, block, dry_run)
            if updated:
                if type(new_block) is not type(block):
                    frameinfo = getframeinfo(currentframe())
                    self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                    self.stdout.write(
                        self.style.WARNING(
                            'ERROR Types Not the same <block_type>:<existing type><new type> - '
                            f'{block.block_type}:{type(block)}:{type(new_block)}'
                        )
                    )
                    sys.exit(-1)
                value[cnt] = new_block
                field_updated = True
            cnt += 1

        return field_updated, value

    def process_list_field(self, page_title, field, value):
        value_updated = False
        enumerate_list = tuple(enumerate(value))
        for index, item in enumerate_list:
            if isinstance(item, str):
                updated, new_item = self.replace_string(page_title, field, item)
                if updated:
                    self.report_page_needs_updating(page_title, field, item)
                    value[index] = new_item
                    value_updated = True
            else:
                frameinfo = getframeinfo(currentframe())
                self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                self.stdout.write(self.style.WARNING(f'Unhandled List Field type: {type(item)}'))
                sys.exit(-1)
        return value_updated, value

    def process_streamchild_field(self, page_title, block, dry_run):  # noqa C901
        block_updated = False
        for child in block.value:
            for field_name in child.value:
                if child.value[field_name]:
                    if isinstance(child.value[field_name], str):
                        updated, new_value = self.replace_string(
                            page_title, field_name, child.value[field_name], dry_run
                        )
                        if updated:
                            child.value[field_name] = new_value
                            block_updated = True
                    elif isinstance(child.value[field_name], RichText):
                        updated, new_source = self.replace_richtextbox(page_title, child.value[field_name].source)
                        if updated:
                            child.value[field_name].source = new_source
                            block_updated = True
                    elif isinstance(child.value[field_name], AltTextImage):
                        updated, new_value = self.process_alttextimage_field(
                            page_title, field_name, child.value[field_name]
                        )
                        if updated:
                            child.value[field_name] = new_value
                            block_updated = True
                    else:
                        frameinfo = getframeinfo(currentframe())
                        self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                        self.stdout.write(
                            self.style.WARNING(f'Unhandled StreamChild field type: {type(child.value[field_name],)}')
                        )
                        sys.exit(-1)

            return block_updated, block

    def update_field(self, page, field, value, dry_run):

        updated = False

        if (
            field == 'specific_class'
            or field == 'specific'
            or isinstance(value, timedelta)
            or isinstance(value, Number)
            or isinstance(value, Decimal)
            or isinstance(value, Fraction)
            or isinstance(value, datetime)
            or isinstance(value, ModelState)
            or isinstance(value, UUID)
        ):
            return False, value

        if not value:
            return False, value

        if isinstance(value, str):
            updated, value = self.process_string_field(page.title, field, value, dry_run)
        elif isinstance(value, StreamValue):
            updated, value = self.process_streamvalue_field(page.title, value, dry_run)
        elif isinstance(value, list):
            updated, value = self.process_list_field(page.title, field, value)
        else:
            frameinfo = getframeinfo(currentframe())
            self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
            self.stdout.write(self.style.WARNING(f'Unhandled Field type: {type(value)}'))
            sys.exit(-1)

        return updated, value

    def update_page(self, page, dry_run):  # noqa C901

        self.stdout.write(self.style.SUCCESS(f'Processing Page: {page.title}'))

        fields = [key for key, value in page.specific.__dict__.items() if not isinstance(value, self.CALLABLES)]

        field_updated = False
        for field_name in fields:
            field_value = page.specific.__dict__[field_name]
            if field_value:
                updated, new_value = self.update_field(page, field_name, field_value, dry_run)
                if updated:
                    if type(field_value) is not type(new_value):
                        frameinfo = getframeinfo(currentframe())
                        self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                        self.stdout.write(
                            self.style.WARNING(
                                'ERROR Types Not the same <field_name>:<existing type><new type> - '
                                ' {field_name}:{type(field_value)}:{type(new_value)}'
                            )
                        )
                        sys.exit(-1)
                    field_updated = True
                    setattr(page, field_name, new_value)
                    self.stdout.write(self.style.SUCCESS(f'UPDATE <page>:<field> - {page.title}:{field_name}'))

        if field_updated and not dry_run:
            try:
                page.specific.save_revision().publish()
            except ValidationError as ve:
                self.stdout.write(self.style.ERROR(f'ERROR Saving Page: {page.title} - {str(ve)}'))
            except RuntimeError as re:
                self.stdout.write(self.style.ERROR(f'ERROR Saving Page: {page.title} - {str(re)}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'ERROR Saving Page: {page.title} - {str(e)}'))

        for child in page.get_children():
            if child.live:
                self.update_page(child, dry_run)

    @transaction.atomic
    def handle(self, *args, **options):  # noqa: C901
        # if settings.APP_ENVIRONMENT.lower() != 'hotfix':
        #     self.stdout.write(self.style.WARNING('Running in env other than hotfix is disabled - exiting'))
        #     return
        hostname = options['hostname']
        dry_run = options['dry_run']

        try:
            site = Site.objects.get(hostname=hostname)
        except Site.DoesNotExist as e:
            self.stderr.write(self.style.ERROR('Site not found'))
            sentry_sdk.capture_exception(e)
            return

        source_root = site.root_page

        pages_to_update = source_root.get_children()

        for page in pages_to_update:
            if page.live:
                self.update_page(page, dry_run=dry_run)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
