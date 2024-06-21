import logging

import requests
from django.conf import settings
from django.core.management import BaseCommand

from core.models import Country

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update Countries ISO codes'

    def handle(self, *args, **options):
        countries = Country.objects.all()
        all_countries = requests.get(settings.COUNTRIES_ISO_CODE_UPDATE_API)
        if all_countries.status_code == 200:
            all_countries_json = all_countries.json()
            for country in countries:
                found = list(filter(lambda x: x['name']['common'] == country.name, all_countries_json))
                if len(found) > 0:
                    country.iso2 = found[0]['cca2']
                    country.save()
        else:
            logger.exception('Failed to download Countries ISO codes')
