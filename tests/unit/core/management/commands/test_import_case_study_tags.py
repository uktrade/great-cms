from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command


@pytest.mark.parametrize('mgm_cmd', [('import_countries_tags'), ('import_regions_tags'), ('import_trading_blocs_tags')])
@pytest.mark.django_db
def test_import_cs_tags(mgm_cmd):
    with patch('core.helpers.get_s3_file_stream') as mock_work_function:
        call_command(mgm_cmd, stdout=StringIO())
        assert mock_work_function.called
