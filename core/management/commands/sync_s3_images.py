from django.core.management import BaseCommand

import json
from django.conf import settings
import requests
from bs4 import BeautifulSoup


class Command(BaseCommand):
    help = 'Used to scrape a give url for all images and dump to json'

    def add_arguments(self, parser):
        parser.add_argument('url_to_scrape', type=str, help='Please add a valid url')

    def handle(self, *args, **options):

        def make_json(json_file_path):
            data = {}

            with open(json_file_path, 'w', encoding='utf-8') as jsonf:
                url = options['url_to_scrape']
                html_page = requests.get(url)
                soup = BeautifulSoup(html_page.content, 'html.parser')
                images = soup.find_all('img')
                data['images'] = [img.get('src') for img in images]
                jsonf.write(json.dumps(data, indent=4))

        json_file_path = settings.ROOT_DIR / 's3_images.json'

        make_json(json_file_path)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
