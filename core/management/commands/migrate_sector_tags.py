from django.core.management import BaseCommand

from core.models import SectorTag, SectorTagged
from domestic.models import CountryGuidePage


class Command(BaseCommand):
    help = 'Populates market guide sector tags from industry tags'

    def handle(self, *args, **options):
        industry_sector_map = {
            'Advanced manufacturing': [],
            'Automotive': ['Automotive'],
            'Agri-technology': ['Technology and smart cities', 'Agriculture, horticulture, fisheries and pets'],
            'Agriculture': ['Agriculture, horticulture, fisheries and pets'],
            'Biotechnology': ['Pharmaceuticals and biotechnology'],
            'Cleantech': ['Technology and smart cities'],
            'Consumer products': ['Consumer and retail'],
            'Cyber security': ['Security', 'Technology and smart cities'],
            'Construction': ['Construction'],
            'E-commerce': ['Consumer and retail'],
            'Energy': ['Energy'],
            'Education': ['Education and training'],
            'Engineering': ['Advanced engineering'],
            'Financial services': ['Financial and professional services'],
            'Fintech': ['Technology and smart cities', 'Financial and professional services'],
            'Fisheries': ['Agriculture, horticulture, fisheries and pets'],
            'Food and drink': ['Food and drink'],
            'Healthcare': ['Healthcare services'],
            'Horticulture': ['Agriculture, horticulture, fisheries and pets'],
            'Infrastructure': [],
            'International organisations': ['Financial and professional services'],
            'Leisure and tourism': ['Consumer and retail'],
            'Life sciences': [],
            'Low carbon': ['Environment'],
            'Luxury': ['Consumer and retail'],
            'Mining': ['Mining'],
            'Nuclear': ['Energy'],
            'Ocean economy': ['Environment'],
            'Offshore wind': ['Energy', 'Environment'],
            'Oil and gas': ['Energy'],
            'Pharmaceuticals': ['Pharmaceuticals and biotechnology'],
            'Professional services': ['Financial and professional services'],
            'Renewables': ['Energy', 'Environment'],
            'Retail': ['Consumer and retail'],
            'Safety': ['Healthcare services'],
            'Security': ['Security'],
            'Smart cities': ['Technology and smart cities'],
            'Sport': ['Sports economy'],
            'Technology': ['Technology and smart cities'],
            'Training': ['Education and training'],
            'Transport': ['Airports', 'Railways'],
        }
        # add only regions name

        markets = CountryGuidePage.objects.all()
        for item in markets:
            item.sector_tags = []
            for tag in item.tags.all():
                sector_tags = industry_sector_map[tag.name]

                for sector in sector_tags:
                    sector_id = list(SectorTag.objects.filter(name=sector))[0].id
                    SectorTagged.objects.create(object_id=item.id, content_type_id=85, tag_id=sector_id)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
