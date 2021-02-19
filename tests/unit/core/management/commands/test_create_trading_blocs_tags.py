from io import StringIO

import pytest
from django.core.management import call_command

from core import models


@pytest.mark.django_db
def test_create_trading_blocs_tags():
    call_command('import_trading_blocs_tags', stdout=StringIO())
    no_of_trading_blocs = models.PersonalisationTradingBlocTag.objects.count()
    assert no_of_trading_blocs == 30
