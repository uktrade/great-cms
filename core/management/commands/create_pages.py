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
        learn_page = factories.ListPageFactory(
            parent=site.root_page,
            title='learn page',
            slug='learn',
            template='learn/learn_page.html',
        )
        factories.DetailPageFactory(
            parent=learn_page,
            title='How to export first step',
            slug='how-to-export-first-step',
            template='learn/how_to_export_first_step.html',
        )
        factories.DetailPageFactory(
            parent=learn_page,
            title='How to export second step',
            slug='how-to-export-second-step',
            template='learn/how_to_export_second_step.html',
        )
        factories.DetailPageFactory(
            parent=learn_page,
            title='How to export third step',
            slug='how-to-export-third-step',
            template='learn/how_to_export_third_step.html',
        )
        self.stdout.write(self.style.SUCCESS('Pages created'))
