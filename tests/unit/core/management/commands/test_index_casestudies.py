from datetime import datetime, timezone
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command

from core.models import CaseStudyRelatedPages
from tests.unit.core.factories import (
    CaseStudyFactory,
    DetailPageFactory,
    TopicPageFactory,
)


@pytest.mark.django_db
def test_index_casestudies(mock_opensearch_get_connection, domestic_homepage):
    hs_codes = ['112233', '11', '1122']
    countries = ['France', 'El Salvador']
    lesson_detail_1 = DetailPageFactory(parent=domestic_homepage, title='lesson 1', estimated_read_duration='0:02:30')
    lesson_topic_1 = TopicPageFactory()
    case_study_1 = CaseStudyFactory(id=1)

    CaseStudyRelatedPages(case_study=case_study_1, page=lesson_detail_1).save()
    CaseStudyRelatedPages(case_study=case_study_1, page=lesson_topic_1).save()
    for code in hs_codes:
        case_study_1.hs_code_tags.add(code)
    for country in countries:
        case_study_1.country_code_tags.add(country)
    case_study_1.save()
    CaseStudyFactory(id=2)

    with patch('opensearch.helpers.bulk') as mock_bulk:
        call_command('index_casestudies', stdout=StringIO())
        assert mock_bulk.called
        cs_1 = mock_bulk.call_args[0][1][1].get('_source')
        cs_2 = mock_bulk.call_args[0][1][0].get('_source')

        assert cs_1.get('lesson') == f'lesson_{lesson_detail_1.id} topic_{lesson_topic_1.id}'
        assert cs_1.get('hscodes') == ' '.join(hs_codes)
        assert cs_1.get('country') == 'France El_Salvador'
        diff = datetime.now(timezone.utc) - cs_1.get('modified')
        assert diff.seconds == 0
        assert cs_1.get('pk') == '1'
        assert cs_2.get('pk') == '2'
