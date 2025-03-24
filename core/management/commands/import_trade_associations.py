import tablib
from django.conf import settings
from django.core.management import BaseCommand

from international_online_offer.models import TradeAssociation


class Command(BaseCommand):
    help = 'Import Trade Associations for Expand Your Business'

    def handle(self, *args, **options):
        with open(settings.ROOT_DIR / 'core/fixtures/trade_associations.csv', 'r', encoding='utf-8') as file:
            data = tablib.import_set(file, format='csv', headers=True)

            for item in data:
                if not TradeAssociation.objects.filter(trade_association_id=item[0]).exists():
                    TradeAssociation.objects.create(
                        trade_association_id=item[0],
                        sector_grouping=item[1],
                        association_name=item[2],
                        website_link=item[3],
                        sector=item[4],
                        brief_description=item[5],
                    )
                else:
                    TradeAssociation.objects.filter(trade_association_id=item[0]).update(
                        trade_association_id=item[0],
                        sector_grouping=item[1],
                        association_name=item[2],
                        website_link=item[3],
                        sector=item[4],
                        brief_description=item[5],
                    )

            self.stdout.write(self.style.SUCCESS('All done with trade associations, bye!'))
