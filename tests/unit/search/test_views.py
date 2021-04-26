import json
from unittest.mock import Mock, patch

import pytest
import requests
from django.urls import reverse


@pytest.mark.django_db
def test_search_view(client):

    """We mock the call to ActivityStream"""

    with patch('search.helpers.search_with_activitystream') as search:
        mock_results = json.dumps(
            {
                'took': 17,
                'timed_out': False,
                '_shards': {'total': 4, 'successful': 4, 'skipped': 0, 'failed': 0},
                'hits': {
                    'total': {
                        'value': 5,
                        'relation': 'eq',
                        # This is an ActivityStream-V2-style/ES7-style 'total' field -
                        # AS-V1/ES6 returned an int not a dict
                    },
                    'max_score': 0.2876821,
                    'hits': [
                        {
                            '_index': 'objects__feed_id_first_feed__date_2019',
                            '_type': '_doc',
                            '_id': 'dit:exportOpportunities:Opportunity:2',
                            '_score': 0.2876821,
                            '_source': {
                                'type': ['Document', 'dit:Opportunity'],
                                'title': 'France - Data analysis services',
                                'content': 'The purpose of this contract is to analyze...',
                                'url': 'www.great.gov.uk/opportunities/1',
                            },
                        },
                        {
                            '_index': 'objects__feed_id_first_feed__date_2019',
                            '_type': '_doc',
                            '_id': 'dit:exportOpportunities:Opportunity:2',
                            '_score': 0.18232156,
                            '_source': {
                                'type': ['Document', 'dit:Opportunity'],
                                'title': 'Germany - snow clearing',
                                'content': 'Winter services for the properties1) Former...',
                                'url': 'www.great.gov.uk/opportunities/2',
                            },
                        },
                    ],
                },
            }
        )
        search.return_value = Mock(status_code=200, content=mock_results)

        response = client.get(reverse('search:search'), data={'q': 'services'})
        context = response.context_data

        assert response.status_code == 200
        assert context['results'] == [
            {
                'type': 'Export opportunity',
                'title': 'France - Data analysis services',
                'content': 'The purpose of this contract is to analyze...',
                'url': 'www.great.gov.uk/opportunities/1',
            },
            {
                'type': 'Export opportunity',
                'title': 'Germany - snow clearing',
                'content': 'Winter services for the properties1) Former...',
                'url': 'www.great.gov.uk/opportunities/2',
            },
        ]

        """ What if there are no results? """
        search.return_value = Mock(
            status_code=200,
            content=json.dumps(
                {
                    'took': 17,
                    'timed_out': False,
                    '_shards': {'total': 4, 'successful': 4, 'skipped': 0, 'failed': 0},
                    'hits': {
                        'total': {
                            'value': 0,
                            'relation': 'eq',
                        },
                        'hits': [],
                    },
                }
            ),
        )

        response = client.get(reverse('search:search'), data={'q': 'services'})
        context = response.context_data

        assert response.status_code == 200
        assert context['results'] == []

        """ What if ActivitySteam sends an error? """
        search.return_value = Mock(status_code=500, content='[service overloaded]')

        response = client.get(reverse('search:search'), data={'q': 'services'})
        context = response.context_data

        assert response.status_code == 200
        # This can be handled on the front end as we wish
        assert context['error_message'] == '[service overloaded]'
        assert context['error_status_code'] == 500

        """ What if ActivitySteam is down? """
        search.side_effect = requests.exceptions.ConnectionError

        response = client.get(reverse('search:search'), data={'q': 'services'})
        context = response.context_data

        assert response.status_code == 200
        # This can be handled on the front end as we wish
        assert context['error_message'] == 'Activity Stream connection failed'
        assert context['error_status_code'] == 500
