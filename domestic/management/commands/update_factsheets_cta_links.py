import argparse
import re

import requests
from django.core.management import BaseCommand, CommandError

from domestic.models import CountryGuidePage

CONTENT_API_FACTSHEETS_LANDING = 'https://www.gov.uk/api/content/government/collections/trade-and-investment-factsheets'


class Command(BaseCommand):
    help = 'Update factsheets CTA links based on gov.uk content API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry_run',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Show summary output only, do not update data',
        )

    def handle(self, *args, **options):  # noqa: C901
        # Get all links from the API
        attachments = []
        landing_page = requests.get(CONTENT_API_FACTSHEETS_LANDING)

        if landing_page.status_code != 200:
            raise CommandError('Could not get data from GOVUK content API.')

        for doc in landing_page.json()['links']['documents']:
            if doc['document_type'] == 'official_statistics':
                collection = requests.get(doc['api_url'])
                if collection.status_code != 200:
                    raise CommandError('Could not get data from GOVUK content API.')
                attachments += collection.json()['details']['attachments']

        updated = 0

        self.stdout.write(f'Loaded {len(attachments)} factsheets details from API')

        parens_regex = re.compile(r'(The |\(.*\)|,.*)')
        for guide in CountryGuidePage.objects.all():
            if guide.intro_cta_three_title != 'View latest trade statistics':
                self.stdout.write(f'{guide.title}: CTA not present or modified, not updating')
            else:
                # Remove extra info in parens or after comma, or any preceding 'The ' (e.g. 'The Netherlands')
                trimmed_title = parens_regex.sub('', guide.title).strip()

                # Ensure name is matched exactly (e.g. do not match 'Indian' for 'India')
                pdf = next((x for x in attachments if re.search(rf'{trimmed_title}(?!\w)', x['title'])), None)

                if pdf is not None:
                    if not options['dry_run']:
                        guide.intro_cta_three_link = pdf['url']
                        guide.save()
                        updated += 1
                else:
                    self.stdout.write(f'{guide.title}: no factsheet found')

        if options['dry_run'] is True:
            self.stdout.write(self.style.WARNING('Dry run -- no data updated.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} Country Guides'))

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
