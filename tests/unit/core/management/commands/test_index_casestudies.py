from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from tests.unit.core.factories import CaseStudyFactory


@pytest.mark.django_db
def test_index_casestudies(mock_elasticsearch_connect, mock_cs_update):
    CaseStudyFactory(id=1)
    CaseStudyFactory(id=2)
    with patch('elasticsearch.helpers.bulk') as mock_bulk:
        call_command('index_casestudies', stdout=StringIO())
        assert mock_bulk.called
        assert mock_bulk.call_args[0][1][0].get('_source').get('pk') == '2'
        assert mock_bulk.call_args[0][1][1].get('_source').get('pk') == '1'
