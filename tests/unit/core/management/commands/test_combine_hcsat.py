from io import StringIO

import pytest
from django.core.management import call_command

from core.models import HCSAT
from export_academy.models import CsatUserFeedback as ExportAcademyHCSAT
from exportplan.models import CsatUserFeedback as ExportPlanHCSAT
from find_a_buyer.models import CsatUserFeedback as FindABuyerHCSAT
from learn.models import CsatUserFeedback as LearnHCSAT
from tests.unit.export_academy.factories import (
    HCSATFactory as ExportAcademyHCSATFactory,
)
from tests.unit.exportplan.factories import HCSATFactory as ExportPlanHCSATFactory
from tests.unit.find_a_buyer.factories import HCSATFactory as FindABuyerHCSATFactory
from tests.unit.learn.factories import HCSATFactory as LearnHCSATFactory


@pytest.mark.django_db
def test_combine_hcsat():
    for x in range(4):
        # Create 4 hcsats in each implementation

        FindABuyerHCSATFactory()
        ExportPlanHCSATFactory()
        ExportAcademyHCSATFactory()
        LearnHCSATFactory()

    assert FindABuyerHCSAT.objects.all().count() == 4
    assert ExportAcademyHCSAT.objects.all().count() == 4
    assert ExportPlanHCSAT.objects.all().count() == 4
    assert LearnHCSAT.objects.all().count() == 4

    call_command('combine_hcsat', stdout=StringIO())

    # This test needs adapting. We want to assert the new HCSAT model has 16 objects

    assert HCSAT.objects.all().count() == 16
