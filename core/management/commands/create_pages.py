from django.core.management import BaseCommand
from wagtail.core.models import Site

import tests.unit.domestic.factories
import tests.unit.exportplan.factories


class Command(BaseCommand):

    def handle(self, *args, **options):
        site = Site.objects.get(pk=1)

        homepage = tests.unit.domestic.factories.DomesticHomePageFactory(parent=site.root_page)
        export_plan = tests.unit.exportplan.factories.ExportPlanPageFactory(
            parent=homepage,
            slug='export-plan'
        )
        tests.unit.exportplan.factories.ExportPlanDashboardPageFactory(
            parent=export_plan,
            slug='dashboard'
        )

        site.root_page = homepage
        site.save()
