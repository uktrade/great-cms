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

    def handle(self, *args, **kwargs):
        for guide in CountryGuidePage.objects.all():

            intro_ctas = guide.intro_ctas

            # Link for export opportunities cannot be derived from existing data,
            # ignore if not already set otherwise reuse
            export_opportunities_cta = next((x for x in intro_ctas if 'live export opportunities' in x['title']), None)
            if export_opportunities_cta:
                guide.intro_cta_one_title = 'View live export opportunities'
                guide.intro_cta_one_link = export_opportunities_cta['link']
            else:
                guide.intro_cta_one_title = ''
                guide.intro_cta_one_link = ''
                print('No export opportunities link found for {}'.format(guide.heading))

            # Link for Export events should be reused if it doesn't match old url. Derive new link otherwise
            export_events_cta = next((x for x in intro_ctas if 'export events' in x['title']), None)
            guide.intro_cta_two_title = 'Find export events'
            if export_events_cta and 'events.great.gov.uk/' not in export_events_cta['link']:
                guide.intro_cta_two_link = export_events_cta['link']
                print('Custom export events link found for {} ({})'.format(guide.heading, export_events_cta['link']))
            else:
                guide.intro_cta_two_link = (
                    'https://www.events.great.gov.uk/ehome/trade-events-calendar/all-events'
                    '/?keyword={}'.format(urllib.parse.quote(guide.heading))
                )

            # Link for factsheet is for now based on start letter of country name
            letter_range = factsheets_links[next(x for x in factsheets_links if guide.heading[0] in x)]
            guide.intro_cta_three_title = 'View trade and investment factsheets'
            guide.intro_cta_three_link = (
                'https://www.gov.uk/government/statistics/trade-and-investment-factsheets'
                '-partner-names-beginning-with-{}'.format(letter_range)
            )

            # Link for online marketplace cannot be derived from existing data,
            # ignore if not already set otherwise reuse
            online_marketplace_cta = next((x for x in intro_ctas if 'Find an online marketplace' in x['title']), None)
            if online_marketplace_cta:
                guide.intro_cta_four_title = 'Find an online marketplace'
                guide.intro_cta_four_link = online_marketplace_cta['link']
            else:
                guide.intro_cta_four_title = ''
                guide.intro_cta_four_link = ''
                print('No online marketplace link found for {}'.format(guide.heading))

            # Link for duties and customs procedures is guide.duties_and_custom_procedures_cta_link,
            if guide.duties_and_custom_procedures_cta_link:
                guide.intro_cta_five_title = 'Check duties and customs'
                guide.intro_cta_five_link = guide.duties_and_custom_procedures_cta_link
            else:
                guide.intro_cta_five_title = ''
                guide.intro_cta_five_link = ''
                print('No duties and customs link found for {}'.format(guide.heading))

            # Link for trade barriers is derived from the linked country iso2 code
            iso2 = getattr(guide.country, 'iso2', None)
            if iso2:
                guide.intro_cta_six_title = 'Check for trade barriers'
                guide.intro_cta_six_link = (
                    'https://www.check-international-trade-barriers.service.gov.uk/barriers'
                    '/?resolved=0&location={}'.format(iso2.lower())
                )
            else:
                guide.intro_cta_six_title = ''
                guide.intro_cta_six_link = ''
                print('No ISO2 code found for {}'.format(guide.heading))

            guide.save()

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
