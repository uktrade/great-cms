import csv
from io import StringIO
from urllib.parse import urlparse

from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction
from wagtail.models import Page




class Command(BaseCommand):
    help = 'Uploads SEO information to Wagtail articles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source', type=str, required=True, help='Source wagtail page (e.g., /bau-homepage-new)'
        )

    @transaction.atomic
    def handle(self, *args, **options):
        source_hostname = options['source']
        print('Ingesting SEO Data')

        with open(
            settings.ROOT_DIR / 'core/fixtures/seo-data.csv', 
            'r',
            encoding='utf-8',
        ) as f:
            for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                # Construct URL path
                url_path = urlparse(row.get('URL')).path
                full_url_path = source_hostname + url_path

                # Get metadata
                seo_title = row.get('Title')
                search_description = row.get('Description') 

                page = Page.objects.live().filter(url_path=full_url_path, locale__language_code='en-gb').first()
                if page:
                    page.seo_title=seo_title
                    page.search_description=search_description
                    page.save()
                    print(f'Updated SEO Title & Description for {url_path}')
            print('Data ingestion finished')        
