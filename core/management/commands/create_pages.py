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
        learn_homepage = factories.ListPageFactory(
            parent=site.root_page,
            title='Learn',
            slug='learn',
            template='learn/learn_page.html',
        )
        factories.DetailPageFactory(
            parent=learn_homepage,
            title='How to export introduction',
            slug='introduction',
            template='learn/learn_introduction.html',
        )
        learn_categories = factories.ListPageFactory(
            parent=learn_homepage,
            title='Learn how to export',
            slug='categories',
            template='learn/landing_page.html',
        )
        factories.DetailPageFactory(
            parent=learn_categories,
            title='Market research',
            slug='market-research',
            template='learn/category.html',
        )
        self.stdout.write(self.style.SUCCESS('Pages created'))
