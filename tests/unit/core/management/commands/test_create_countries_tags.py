from io import StringIO

import pytest
from django.core.management import call_command

from core import models


@pytest.mark.django_db
def test_create_countries_tags():
    call_command('import_countries_tags', stdout=StringIO())
    no_of_countries = models.PersonalisationCountryTag.objects.count()
    assert no_of_countries == 194
