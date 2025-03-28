import csv
from io import StringIO

import pytest
from faker import Faker

from domestic_growth.admin import DomesticGrowthContentDjangoAdminModel
from domestic_growth.models import DomesticGrowthContent


@pytest.mark.django_db
def test_domestic_growth_content_snippets_created_from_csv():
    fake = Faker()

    output = StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(['Snippet ID', 'Title', 'Description', 'URL', 'Dynamic', 'Region', 'Sector'])

    # Data rows
    writer.writerow(['A01', fake.word(), fake.paragraph(nb_sentences=2), fake.url(), 'Y', 'London', 'Automotive'])
    writer.writerow(
        ['B02', fake.word(), fake.paragraph(nb_sentences=2), fake.url(), '', 'Northern Ireland', 'Food and drink']
    )
    writer.writerow(['B03', fake.word(), fake.paragraph(nb_sentences=2), fake.url(), '', 'East Midlands', 'Mining'])
    writer.writerow(['B03', fake.word(), fake.paragraph(nb_sentences=2), fake.url(), '', 'Edinburgh', 'Banking'])

    # Get the CSV data
    csv_content = csv.reader(output.getvalue().splitlines())

    admin_model = DomesticGrowthContentDjangoAdminModel(DomesticGrowthContent, None)
    num_imported_or_modified, errored = admin_model.import_domestic_growth_content_snippets(csv_content)

    assert num_imported_or_modified == 4

    # B03 should have been modified
    assert DomesticGrowthContent.objects.count() == 3
    snippet_b03 = DomesticGrowthContent.objects.get(content_id='B03')
    assert snippet_b03.sector == 'Banking'
    assert snippet_b03.region == 'Edinburgh'
