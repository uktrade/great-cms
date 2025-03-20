import csv
from io import StringIO

from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction
from wagtail.models import Page


class Command(BaseCommand):
    help = 'Uploads SEO information to Wagtail articles'

    def handle(self, *args, **options):
        with open(
            settings.ROOT_DIR / 'core/fixtures/seo-data.csv', 
            'r',
            encoding='utf-8',
        ) as f:
            with transaction.atomic():
                for row in csv.DictReader(StringIO(f.read()), delimiter=','):
                    url_path = row.get('url_path')
                    seo_title = row.get('seo_title')
                    search_description = row.get('search_description') 

                    page = Page.objects.live().filter(url_path=url_path).first()
                    if page:
                        page.update(
                            seo_title=seo_title,
                            search_description=search_description
                        )
