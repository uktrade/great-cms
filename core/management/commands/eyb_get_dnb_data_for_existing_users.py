from django.core.management import BaseCommand
from requests.exceptions import HTTPError

from international_online_offer.dnb.api import company_list_search
from international_online_offer.models import UserData


class Command(BaseCommand):
    help = 'Retrieves Dunn and Bradstreet data and updates existing EYB UserData where there is only one match.'

    def handle(self, *args, **options):
        users = UserData.objects.all()
        total_matched = 0
        total_users = len(users)

        self.stdout.write(self.style.SUCCESS(f'Running dnb matcher for existing eyb users (N={total_users})'))

        for user in users:
            if not user.duns_number and user.company_name and user.company_location:
                try:
                    duns_matches = company_list_search(
                        {'searchTerm': user.company_name, 'countryISOAlpha2Code': user.company_location}
                    )

                    # only use duns info if there is exactly one match
                    if duns_matches.get('total_matches', 0) == 1:
                        match = duns_matches['results'][0]
                        user.duns_number = match['duns_number']
                        user.address_line_1 = match['address_line_1']
                        user.address_line_2 = match['address_line_2']
                        user.town = match['address_town']
                        user.county = match['address_country']
                        user.postcode = match['address_postcode']
                        user.company_website = match['domain']
                        user.save()
                        total_matched += 1
                except HTTPError:
                    self.stdout.write(
                        self.style.ERROR(f'API error for company {user.company_name} location {user.company_location}')
                    )

        self.stdout.write(
            self.style.SUCCESS(f'Matched {total_matched}/{total_users} ({round((total_matched/total_users)*100,2)}%)')
        )
