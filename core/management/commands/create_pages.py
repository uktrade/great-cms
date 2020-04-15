from django.core.management import BaseCommand
from wagtail.core.models import Site

from tests.unit.core import factories


class Command(BaseCommand):

    def handle(self, *args, **options):
        site = Site.objects.first()
        export_plan = factories.ListPageFactory(
            parent=site.root_page,
            title='export plan',
            slug='export-plan',
            template='exportplan/export_plan_page.html',
        )
        factories.DetailPageFactory(
            parent=export_plan,
            title='export plan dashboard',
            slug='dashboard',
            template='exportplan/export_plan_dashboard_page.html',
        )
        self.stdout.write(self.style.SUCCESS('Pages created'))
