import uuid

import sentry_sdk
from django.core.management.base import BaseCommand
from django.db import transaction
from wagtail.models import Site


class Command(BaseCommand):
    help = 'Copy wagtail pages from one site to another'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source', type=str, required=True, help='Source site hostname (e.g., www.dev.great.uktrade.digital)'
        )
        parser.add_argument(
            '--dest', type=str, required=True, help='Destination site hostname (e.g., www.dev.bgs.uktrade.digital)'
        )
        parser.add_argument('--skip-root', action='store_true', help='Skip copying the root page')

    def copy_with_safe_paths(self, source_page, destination_parent):

        try:
            temp_slug = f'{source_page.slug}-{uuid.uuid4().hex[:8]}'

            new_page = source_page.specific.copy(
                recursive=False,
                to=destination_parent,
                update_attrs={
                    'slug': temp_slug,
                    'title': source_page.title,
                },
                keep_live=False,
            )

            # Revert slug to original
            new_page.slug = source_page.slug
            new_page.save()

            # publish if it's live
            if source_page.live:
                revision = new_page.save_revision()
                revision.publish()

            for child in source_page.get_children():
                self.copy_with_safe_paths(child, new_page)

            return new_page
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to copy {source_page.title} (ID: {source_page.id}): {str(e)}'))
            sentry_sdk.capture_exception(e)

    @transaction.atomic
    def handle(self, *args, **options):
        source_hostname = options['source']
        dest_hostname = options['dest']
        skip_root = options['skip_root']

        try:
            source_site = Site.objects.get(hostname=source_hostname)
            dest_site = Site.objects.get(hostname=dest_hostname)
        except Site.DoesNotExist as e:
            self.stderr.write(self.style.ERROR('Site not found'))
            sentry_sdk.capture_exception(e)
            return

        source_root = source_site.root_page
        dest_root = dest_site.root_page

        if skip_root:
            pages_to_copy = source_root.get_children()
            self.stdout.write(f'Copying {len(pages_to_copy)} first-level pages and their dependents')
        else:
            pages_to_copy = [source_root]
            self.stdout.write('Copying entire tree including root')

        # Delete pages if they exist
        for page in dest_root.get_children():
            self.stdout.write(f'Deleting existing page: {page.title}')
            page.delete()

        for page in pages_to_copy:
            self.copy_with_safe_paths(source_page=page, destination_parent=dest_root)

        self.stdout.write(self.style.SUCCESS('Copy operation complete'))
