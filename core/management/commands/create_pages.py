from django.core.management import BaseCommand
from wagtail.core.models import Site

import tests.unit.exportplan.factories
import tests.unit.core.factories
import tests.unit.learn.factories


class Command(BaseCommand):

    def handle(self, *args, **options):
        site = Site.objects.first()
        export_plan = tests.unit.exportplan.factories.ExportPlanPageFactory(parent=site.root_page)
        tests.unit.exportplan.factories.ExportPlanDashboardPageFactory(parent=export_plan)
        tests.unit.core.factories.PersonalisedPageFactory(parent=site.root_page, slug='country', title='Country')
        tests.unit.learn.factories.LearnPageFactory(parent=site.root_page, slug='learn')

        self.stdout.write(self.style.SUCCESS('Pages created'))
