import argparse
import re
import sys
from datetime import datetime
from inspect import currentframe, getframeinfo

from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models.fields import Field
from wagtail.blocks.field_block import CharBlock, RichTextBlock
from wagtail.blocks.stream_block import StreamBlock, StreamValue
from wagtail.blocks.struct_block import StructValue
from wagtail.rich_text import RichText
from wagtail.snippets.models import SNIPPET_MODELS

from core.blocks import CaseStudyQuoteBlock, LinkStructValue
from core.models import AltTextImage, Country, GreatMedia, IndustryTag, Region, Tag


class Command(BaseCommand):
    help = 'Update Snippets for given site'

    string_to_replace = 'great.gov.uk'
    replacement_string = ''

    def add_arguments(self, parser):
        parser.add_argument(
            '--replacement',
            type=str,
            required=True,
            help='String to replace with replacement i.e <stringtoreplace>:<replacement>',
        )
        parser.add_argument(
            '--dry_run',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Show summary output only, do not update data',
        )

    def string_contains_html(self, value):
        return bool(BeautifulSoup(value, 'html.parser').find())

    def process_string(self, field_value):  # noqa C901

        updated = False
        value = field_value

        if self.string_contains_html(field_value):
            updated, new_source = self.replace_richtextbox(field_value)
            return updated, new_source
        else:
            positions = [i for i in range(len(value)) if value.startswith(self.string_to_replace, i)]
            if positions:
                for pos in positions:
                    start = pos - len('event.')
                    if value[start:pos] != 'event.':
                        if value[pos : pos + len(self.string_to_replace)] == self.string_to_replace:  # noqa E203
                            value = (
                                value[:pos]
                                + self.replacement_string
                                + value[pos + len(self.string_to_replace) :]  # noqa E203
                            )
                            updated = True

        return updated, value

    def replace_richtextbox_text(self, source):

        updated = False
        soup = BeautifulSoup(source, 'html.parser')

        findall = soup.find_all(text=re.compile(self.string_to_replace))
        for text in findall:
            fixed_link = text.replace(self.string_to_replace, self.replacement_string)
            text.replace_with(fixed_link)
            updated = True

        return updated, str(soup)

    def replace_richtextbox_links(self, source):
        updated = False
        soup = BeautifulSoup(source, 'html.parser')
        a_tags = soup.find_all('a', href=True)
        for tag in a_tags:
            if self.string_to_replace in tag['href']:
                tag['href'] = tag['href'].replace(self.string_to_replace, self.replacement_string)
                updated = True
        return updated, str(soup)

    def replace_richtextbox(self, field_value):
        snippet_updated = False
        source = field_value
        updated, source = self.replace_richtextbox_text(source)
        if updated:
            snippet_updated = True
        updated, source = self.replace_richtextbox_links(source)
        if updated:
            snippet_updated = True

        return snippet_updated, source

    def process_richtext_block(self, source):
        updated, new_source = self.replace_richtextbox(source)
        return updated, new_source

    def process_stream_block(self, block):
        snippet_updated = False

        new_block = block
        if isinstance(block, StreamValue):
            updated, new_block = self.process_streamvalue_field(block)
            if updated:
                snippet_updated = True
        elif isinstance(block, StreamValue.StreamChild):
            updated, new_block = self.process_streamchild_field(block)
            if updated:
                snippet_updated = True
        else:
            frameinfo = getframeinfo(currentframe())
            self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
            self.stdout.write(self.style.WARNING(f'Unhandled Block Type: {type(block)}'))
            sys.exit(-1)

        return snippet_updated, new_block

    def process_alttextimage_field(self, field_value):
        snippet_updated = False
        alt_text = field_value.alt_text
        if alt_text:
            updated, new_alt_text = self.process_string(alt_text)
            if updated:

                snippet_updated = True
                field_value.alt_text = new_alt_text

        return snippet_updated, field_value

    def process_greatmedia_field(self, block):  # noqa C901

        block_updated = False

        if block.description:
            updated, new_value = self.process_string(block.description)
            if updated:

                block.description = new_value
                block_updated = True

        if block.transcript:
            updated, new_value = self.process_string(block.transcript)
            if updated:

                block.transcript = new_value
                block_updated = True

        if block.subtitles_en:
            updated, new_value = self.process_string(block.subtitles_en)
            if updated:

                block.subtitles_en = new_value
                block_updated = True

        return block_updated, block

    def process_casestudyquoteblock_block(self, block):
        snippet_updated = False
        for field_name, field_value in block.value.items():
            if isinstance(field_value, str):
                updated, new_value = self.process_string(field_value)
                if updated:

                    block[field_name] = new_value
                    snippet_updated = True
            elif isinstance(field_value, StreamValue):
                updated, new_value = self.process_streamvalue_field(field_value)
                if updated:
                    block[field_name] = new_value
                    snippet_updated = True
            else:
                frameinfo = getframeinfo(currentframe())
                self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                self.stdout.write(self.style.WARNING(f'Unhandled Field type: {type(field_value)}'))
                sys.exit(-1)
        return snippet_updated, block

    def process_charblock_block(self, block):
        snippet_updated = False
        updated, new_value = self.process_string(block.value)
        if updated:

            snippet_updated = True
            block.value = new_value
        return snippet_updated, block

    def process_block(self, block):  # noqa C901

        snippet_updated = False

        new_block = block

        if block.block_type == 'content_module':
            return False, block

        if isinstance(block.block, RichTextBlock):
            updated, new_source = self.process_richtext_block(block.value.source)
            if updated:
                new_block.value.source = new_source
                snippet_updated = True
        elif isinstance(block.block, StreamBlock):
            updated, new_block = self.process_stream_block(block)
            if updated:
                snippet_updated = True
        elif isinstance(block.block, CharBlock):
            updated, new_block = self.process_charblock_block(block)
            if updated:
                snippet_updated = True
        elif isinstance(block.block, CaseStudyQuoteBlock):
            updated, new_block = self.process_casestudyquoteblock_block(block)
            if updated:
                snippet_updated = True
        else:
            frameinfo = getframeinfo(currentframe())
            self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
            self.stdout.write(self.style.WARNING(f'Unhandled Block type: {type(block.block)}'))
            sys.exit(-1)
        return snippet_updated, new_block

    def process_streamvalue_field(self, value):
        snippet_updated = False
        cnt = 0
        for block in value:
            if block.block_type.lower() in ('page',):
                cnt += 1
                continue
            updated, new_block = self.process_block(block)
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
                snippet_updated = True
            cnt += 1

        return snippet_updated, value

    def process_structvalue_block(self, block):  # noqa C901
        block_updated = False
        for field_name, field_value in block.items():
            if field_value:
                if isinstance(field_value, str):
                    updated, new_value = self.process_string_field(field_value)
                    if updated:

                        setattr(block, field_name, new_value)
                        block_updated = True
                elif isinstance(field_value, LinkStructValue):
                    for ln, lv in field_value.items():
                        if lv:
                            updated, new_value = self.process_string_field(
                                lv,
                            )
                            if updated:

                                block[field_name][ln] = new_value
                                block_updated = True
                elif isinstance(field_value, StructValue):
                    updated, new_value = self.process_structvalue_block(block)
                    if updated:
                        setattr(block, field_name, new_value)
                        block_updated = True
                elif isinstance(field_value, GreatMedia):
                    updated, new_value = self.process_greatmedia_field(field_value)
                    if updated:

                        block.value[field_name] = new_value
                        block_updated = True
                elif isinstance(field_value, bool):
                    continue
                else:
                    frameinfo = getframeinfo(currentframe())
                    self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                    self.stdout.write(self.style.WARNING(f'Unhandled Block Type: {type(field_value)}'))
                    sys.exit(-1)

        return block_updated, block

    def process_streamchild_field(self, block):  # noqa C901
        snippet_updated = False
        cnt = 0
        for child in block.value:
            if child.value:
                if isinstance(child.value, str):
                    updated, new_value = self.process_string(child.value)
                    if updated:

                        block.value[cnt] = new_value
                        snippet_updated = True
                elif isinstance(child.value, RichText):
                    updated, new_source = self.replace_richtextbox(child.value.source)
                    if updated:

                        block.value[cnt].source = new_source
                        snippet_updated = True
                elif isinstance(child.value, AltTextImage):
                    updated, new_value = self.process_alttextimage_field(child.value)
                    if updated:

                        block.value[cnt] = new_value
                        snippet_updated = True
                elif isinstance(child.value, StructValue):
                    updated, new_value = self.process_structvalue_block(child.value)
                    if updated:

                        block.value[cnt] = new_value
                        snippet_updated = True
                else:
                    frameinfo = getframeinfo(currentframe())
                    self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                    self.stdout.write(self.style.WARNING(f'Unhandled StreamChild field type: {type(child.value)}'))
                    sys.exit(-1)

                cnt += 1
        return snippet_updated, block

    def process_snippet(self, instance, field_names):  # noqa C901

        snippet_updated = False

        for field_name in field_names:
            field_value = getattr(instance, field_name)
            if not field_value:
                continue
            elif isinstance(field_value, bool) or isinstance(field_value, datetime):
                continue
            elif isinstance(field_value, str):
                updated, new_value = self.process_string(field_value)
                if updated:
                    snippet_updated = True
                    setattr(instance, field_name, new_value)
            elif isinstance(field_value, StreamValue):
                updated, new_value = self.process_streamvalue_field(field_value)
                if updated:
                    snippet_updated = True
                    setattr(instance, field_name, new_value)
            else:
                frameinfo = getframeinfo(currentframe())
                self.stdout.write(self.style.WARNING(f'LINE NUMBER {frameinfo.lineno}'))
                self.stdout.write(self.style.WARNING(f'Unhandled Field type: {type(field_value)}'))
                sys.exit(-1)

        return snippet_updated

    @transaction.atomic
    def handle(self, *args, **options):

        dry_run = options['dry_run']
        replacement = options['replacement']

        self.string_to_replace = replacement.split(':')[0]
        self.replacement_string = replacement.split(':')[1]

        for snippet_model in SNIPPET_MODELS:

            if (
                snippet_model is Country
                or snippet_model is IndustryTag
                or snippet_model is Region
                or snippet_model is Tag
            ):
                continue

            instances = snippet_model.objects.all()

            if instances.count() < 1:
                continue

            field_names = [
                field.name
                for field in snippet_model._meta.get_fields()
                if isinstance(field, Field)
                and field.name
                not in (
                    'type',
                    'id',
                    'tags',
                    'hide_title',
                    'image',
                    'slug',
                    'created',
                    'modified',
                    'seo_title',
                    'hs_code_tags',
                    'country_code_tags',
                    'region_code_tags',
                    'trading_bloc_code_tags',
                    'document',
                    'country_tags',
                    'sector_tags',
                    'meta_label',
                    'exporter_type',
                    'index_entries',
                    'region_tags',
                    'trading_bloc_tags',
                    'past_event_presentation_file',
                    'format',
                    'types',
                    'external_id',
                    'start_date',
                    'end_date',
                    'video_recording',
                    'past_event_recorded_date',
                    'past_event_video_recording',
                    'completed',
                    'completed_email_sent',
                    'live',
                    'closed',
                    'is_essential',
                    'is_simple',
                    'is_difficult',
                    'is_goods',
                    'is_services',
                    'content_id',
                    'is_dynamic',
                    'show_image',
                    'task_id',
                    'is_permanent',
                    'automatically_created',
                    'created_at',
                    'redirect_page',
                    'site',
                )
            ]

            for instance in instances:
                self.stdout.write(self.style.SUCCESS(f'Processing Model:Snippet: {snippet_model}:{instance}'))
                updated = self.process_snippet(instance, field_names)
                if updated and not dry_run:
                    self.stdout.write(
                        self.style.SUCCESS(f'Updated Snippet Instance:Snippet: {snippet_model}:{instance}')
                    )
                    instance.save()
                elif updated:
                    self.stdout.write(
                        self.style.SUCCESS(f'Would Update Snippet Instance:Snippet: {snippet_model}:{instance}')
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(f'Would NOT Update Snippet Instance:Snippet: {snippet_model}:{instance}')
                    )

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
