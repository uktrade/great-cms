from django.core.management import BaseCommand

from wagtail.models import Site


class Command(BaseCommand):
    help = 'Used to remove sites from wagtail and create one for local dev with the host "greatcms.trade.great"'

    def handle(self, *args, **options):

        site = Site.objects.first()
        site.delete()

        site = Site.objects.last()
        site.hostname = 'greatcms.trade.great'
        site.port = '8020'
        site.save()
