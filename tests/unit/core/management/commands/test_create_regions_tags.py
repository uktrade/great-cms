from io import StringIO

import pytest
from django.core.management import call_command

from core import models


@pytest.mark.django_db
def test_create_regions_tags():
    call_command('import_regions_tags', stdout=StringIO())
    no_of_regions = models.PersonalisationRegionTag.objects.count()
    assert no_of_regions == 8
