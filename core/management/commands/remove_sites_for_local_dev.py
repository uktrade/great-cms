from django.core.management import BaseCommand

from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Used to remove sites from wagtail and create one for local dev with the host "greatcms.trade.great"'

    def handle(self, *args, **options):

        for model in Site.objects.all():
            model.delete()

        site, create = Site.objects.get_or_create(
            domain='greatcms.trade.great'
            port='8021'
        )

