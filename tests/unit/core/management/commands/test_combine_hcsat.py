from io import StringIO
import pytest
from django.core.management import call_command

from find_a_buyer.models import CsatUserFeedback as FAB
from export_academy.models import CsatUserFeedback as EXAC
from exportplan.models import CsatUserFeedback as EXP
from learn.models import CsatUserFeedback as LEARN

from tests.unit.find_a_buyer.factories import HCSATFactory as FABHCSATFactory
from tests.unit.exportplan.factories import HCSATFactory as EXPHCSATFactory
from tests.unit.export_academy.factories import HCSATFactory as EXACHCSATFactory
from tests.unit.learn.factories import HCSATFactory as LEARNHCSATFactory

@pytest.mark.django_db
def test_combine_hcsat():

    for x in range(4):

        #Create 4 hcsats in each implementation

        FABHCSATFactory()
        EXPHCSATFactory()
        EXACHCSATFactory()
        LEARNHCSATFactory()

    assert FAB.objects.all() == 4
    assert EXAC.objects.all() == 4
    assert EXP.objects.all() == 4
    assert LEARN.objects.all() == 4

    call_command('combine_hcsat', stdout=StringIO())

    # This test needs adapting. We want to assert the new HCSAT model has 16 objects

    assert FAB.objects.all() == 4
    assert EXAC.objects.all() == 4
    assert EXP.objects.all() == 4
    assert LEARN.objects.all() == 4

    # Calling agin should not add anymore objects
    call_command('combine_hcsat', stdout=StringIO())

    # This test needs adapting. We want to assert the new HCSAT model has 16 objects

    assert FAB.objects.all() == 4
    assert EXAC.objects.all() == 4
    assert EXP.objects.all() == 4
    assert LEARN.objects.all() == 4