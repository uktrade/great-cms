import csv
import json

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = 'Convert sic/sectors csv to json'

    def handle(self, *args, **options):
        def make_json(csv_file_path, json_file_path):

            data = {'data': []}

            with open(csv_file_path, encoding='utf-8') as csvf:
                csv_reader = csv.DictReader(csvf)

                for rows in csv_reader:

                    sic_dict = {
                        '_id': rows['_id'],
                        'dit_sector_list_field_04': rows['dit_sector_list_field_04'],
                        'dit_sector_list_full_sector_name': rows['dit_sector_list_full_sector_name'],
                        'exporter_type': rows['exporter_type'],
                        'mapping_id': rows['mapping_id'],
                        'sic_code': rows['sic_code'],
                        'sic_description': rows['sic_description'],
                    }

                    if rows['keywords']:
                        sic_dict['keywords'] = rows['keywords']

                    data['data'].append(sic_dict)

            with open(json_file_path, 'w', encoding='utf-8') as jsonf:
                jsonf.write(json.dumps(data, indent=4))

        csv_file_path = settings.ROOT_DIR / 'core/fixtures/sectors-and-sic-sectors.csv'
        json_file_path = settings.ROOT_DIR / 'core/fixtures/sectors-and-sic-sectors.json'

        make_json(csv_file_path, json_file_path)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
