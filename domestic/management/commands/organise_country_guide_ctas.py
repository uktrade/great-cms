import argparse
import urllib.parse

from django.core.management import BaseCommand

from domestic.models import CountryGuidePage

factsheets_links = {
    'AB': 'a-or-b',
    'CDEF': 'c-to-f',
    'GHI': 'g-to-i',
    'JKL': 'j-to-l',
    'MNO': 'm-to-o',
    'PQR': 'p-to-r',
    'S': 's',
    'TUV': 't-to-v',
    'WXYZ': 'w-to-z',
}


class Command(BaseCommand):
    help = 'Update, set defaults and reorder Country Guide CTAs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry_run',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Show summary output only, do not update data',
        )

    def handle(self, *args, **options):  # noqa: C901
        def dry_print(message):
            if options['dry_run']:
                self.stdout.write(message)

        updated = 0

        for guide in CountryGuidePage.objects.all():
            intro_ctas = guide.intro_ctas

            # Link for export opportunities cannot be derived from existing data,
            # ignore if not already set otherwise reuse
            export_opportunities_cta = next((x for x in intro_ctas if 'live export opportunities' in x['title']), None)
            if export_opportunities_cta:
                guide.intro_cta_one_title = 'View export opportunities'
                guide.intro_cta_one_link = export_opportunities_cta['link']
            else:
                guide.intro_cta_one_title = ''
                guide.intro_cta_one_link = ''
                dry_print(f'{guide.heading}: no export opportunities link found')

            # Link for Export events should be reused if it doesn't match old url. Derive new link otherwise
            export_events_cta = next((x for x in intro_ctas if 'export events' in x['title']), None)
            guide.intro_cta_two_title = 'Find latest export events'
            if export_events_cta and 'events.great.gov.uk/' not in export_events_cta['link']:
                guide.intro_cta_two_link = export_events_cta['link']
                dry_print(f'{guide.heading}: found custom export events link ({guide.intro_cta_two_link})')
            else:
                guide.intro_cta_two_link = f'https://www.events.great.gov.uk/ehome/trade-events-calendar/all-events/?keyword={urllib.parse.quote(guide.heading)}'  # noqa

            # Link for factsheet is for now based on start letter of country name
            letter_range = factsheets_links[next(x for x in factsheets_links if guide.heading[0] in x)]
            guide.intro_cta_three_title = 'View latest trade statistics'
            guide.intro_cta_three_link = f'https://www.gov.uk/government/statistics/trade-and-investment-factsheets-partner-names-beginning-with-{letter_range}'  # noqa

            # Link for online marketplace cannot be derived from existing data,
            # ignore if not already set otherwise reuse
            online_marketplace_cta = next((x for x in intro_ctas if 'Find an online marketplace' in x['title']), None)
            if online_marketplace_cta:
                guide.intro_cta_four_title = 'Find an online marketplace'
                guide.intro_cta_four_link = online_marketplace_cta['link']
            else:
                guide.intro_cta_four_title = ''
                guide.intro_cta_four_link = ''
                dry_print(f'{guide.heading}: no online marketplace link found')

            if options['dry_run'] is False:
                guide.save()

            updated += 1

        if options['dry_run'] is True:
            self.stdout.write(self.style.WARNING('Dry run -- no data updated.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated} Country Guides'))

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
