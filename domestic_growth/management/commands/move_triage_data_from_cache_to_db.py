from django.core.cache import cache
from django.core.management import BaseCommand
from django.db.models.base import Model

from domestic_growth.helpers import persist_to_db
from domestic_growth.models import ExistingBusinessTriage, StartingABusinessTriage


class Command(BaseCommand):
    help = 'Moves incomplete triage data (e.g. if user drops off) from cache to db'

    def handle(self, *args, **options):
        starting_a_business_triage_cache_keys = cache.iter_keys('bgs:StartingABusinessTriage:*')

        for key in starting_a_business_triage_cache_keys:
            self.save(key, StartingABusinessTriage)
            cache.delete(key)

        existing_business_triage_keys = cache.iter_keys('bgs:ExistingBusinessTriage:*')

        for key in existing_business_triage_keys:
            self.save(key, ExistingBusinessTriage)
            cache.delete(key)

    def save(self, key: str, model: Model):
        triage_uuid = key[key.find(':', 7) + 1 :]  # NOQA: E203
        persist_to_db(key, model, triage_uuid)
