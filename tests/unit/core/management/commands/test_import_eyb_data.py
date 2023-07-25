from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command


@pytest.mark.parametrize(
    'mgm_cmd', [('eyb_import_trade_associations'), ('eyb_import_salary_data'), ('eyb_import_rent_data')]
)
@pytest.mark.django_db
def test_import_eyb_data(mgm_cmd):
    with patch('core.helpers.get_s3_file_stream') as mock_work_function:
        call_command(mgm_cmd, stdout=StringIO())
        assert mock_work_function.called
