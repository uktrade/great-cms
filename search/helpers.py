import json
from datetime import date
from math import ceil

import requests
import sentry_sdk
from django.conf import settings
from django.core.paginator import Paginator
from mohawk import Sender
from wagtail.models import Page

from search import serializers

RESULTS_PER_PAGE = 10


def sanitise_page(page):
    try:
        return int(page) if int(page) > 0 else 1
    except (TypeError, ValueError):
        return 1


def parse_results(response, query, page):
    current_page = int(page)
    content = json.loads(response.content)

    if 'error' in content:
        sentry_sdk.capture_message(f"There was an error in /search: {content['error']}")
        return {'search_results': None}
    else:
        full_search_results = serializers.parse_search_results(content)
        paginator = Paginator(full_search_results, RESULTS_PER_PAGE)
        page_obj = paginator.get_page(current_page)
        elided_page_range = [
            page_num
            for page_num in page_obj.paginator.get_elided_page_range(page_obj.number, on_each_side=1, on_ends=1)
        ]
    return {
        'search_results': full_search_results,
        'page_obj': page_obj,
        'elided_page_range': elided_page_range,
    }


def format_query(query, page):
    """Formats query for OpenSearch

    NB: While Great V1 and V2 co-exist, we deliberately only want Article and Services
    to be namespaced for dit:greatCms, to avoid conflicts with documents with the type
    'Article' or 'Services' or 'dit:Article' or 'dit:Services', which will be from
    Great V1, whereas V2's content is namespaced ONLY with dit:greatCms

    """
    from_result = (page - 1) * RESULTS_PER_PAGE
    formatted_query = {
        'query': {
            'function_score': {
                'query': {
                    'bool': {
                        'must': {
                            'bool': {
                                'should': [
                                    {
                                        'match': {
                                            'name': {
                                                'query': query,
                                                'minimum_should_match': '2<75%',
                                            }
                                        }
                                    },
                                    {
                                        'match': {
                                            'content': {
                                                'query': query,
                                                'minimum_should_match': '2<75%',
                                            }
                                        }
                                    },
                                    {
                                        'match': {
                                            'keywords': query,
                                        }
                                    },
                                    {
                                        'match': {
                                            'type': query,
                                        }
                                    },
                                ]
                            }
                        },
                        'filter': [
                            {
                                'bool': {
                                    'should': [
                                        {
                                            'terms': {
                                                'type': [
                                                    'Market',
                                                    'dit:Market',
                                                    'dit:greatCms:Article',
                                                    'dit:greatCms:Service',
                                                    'dit:greatCms:Microsite',
                                                ],
                                            },
                                        },
                                        {
                                            'bool': {
                                                'must': [
                                                    {
                                                        'terms': {
                                                            'type': [
                                                                'Opportunity',
                                                                'dit:Opportunity',
                                                            ],
                                                        },
                                                    },
                                                    {
                                                        'range': {
                                                            'endTime': {
                                                                'gte': date.today().strftime('%Y-%m-%d'),
                                                            },
                                                        },
                                                    },
                                                ],
                                            },
                                        },
                                    ],
                                },
                            },
                        ],
                    }
                },
                'functions': [
                    {
                        'filter': {
                            'terms': {
                                'type': ['dit:greatCms:Service'],
                            }
                        },
                        'weight': 4000,
                    },
                    {
                        'filter': {
                            'terms': {
                                'type': ['dit:greatCms:Article'],
                            }
                        },
                        'weight': 400,
                    },
                    {
                        'filter': {
                            'terms': {
                                'type': ['dit:greatCms:Microsite'],
                            }
                        },
                        'weight': 400,
                    },
                    {
                        'filter': {
                            'terms': {
                                'type': ['Market', 'dit:Market'],
                            }
                        },
                        'weight': 200,
                    },
                ],
                'boost': 10,
                'boost_mode': 'multiply',
            }
        },
        'from': from_result,
        'size': RESULTS_PER_PAGE,
    }

    return json.dumps(formatted_query)


def search_with_activitystream(query):
    """Searches ActivityStream services with given Opensearch query.
    Note that this must be at root level in SearchView class to
    enable it to be mocked in tests.
    """
    request = requests.Request(
        method='GET',
        url=settings.ACTIVITY_STREAM_URL,
        data=query,
    ).prepare()

    auth = Sender(
        {
            'id': settings.ACTIVITY_STREAM_ACCESS_KEY_ID,
            'key': settings.ACTIVITY_STREAM_SECRET_KEY,
            'algorithm': 'sha256',
        },
        settings.ACTIVITY_STREAM_URL,
        'GET',
        content=query,
        content_type='application/json',
    ).request_header

    # Note that the X-Forwarded-* items are overridden by Gov PaaS values
    # in production, and thus the value of ACTIVITY_STREAM_IP_ALLOWLIST
    # in production is irrelevant. It is included here to allow the app to
    # run locally or outside of Gov PaaS.
    request.headers.update(
        {
            'X-Forwarded-Proto': 'https',
            'X-Forwarded-For': settings.ACTIVITY_STREAM_IP_ALLOWLIST,
            'Authorization': auth,
            'Content-Type': 'application/json',
        }
    )

    return requests.Session().send(request)
