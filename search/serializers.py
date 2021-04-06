from functools import partial
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from django.utils.text import Truncator

from directory_constants import urls

build_events_url = partial(urljoin, urls.domestic.EVENTS)


def _strip_html(result):
    # Note: in V1, we used to get markdown back from the search index
    # which we converted into HTML
    html = result.get('content', '')
    result['content'] = ''.join(
        BeautifulSoup(html, 'html.parser').findAll(text=True),
    ).rstrip()


def _abridge_long_contents(result):
    if 'content' in result:
        result['content'] = Truncator(result['content']).chars(160)


def _format_display_type(result):
    mappings = {
        # These do not come from great-cms:
        'Opportunity': 'Export opportunity',
        'dit:Opportunity': 'Export opportunity',
        'Market': 'Online marketplace',
        'dit:Market': 'Online marketplace',
        # NB: While Great V1 and V2 co-exist, we deliberately only want Article and Services
        # namespaced for dit:greatCms so that we don't get documents with the type
        # 'Article' or 'Services' or 'dit:Article' or 'dit:Services', which will be
        # from Great V1, whereas V2's content is namespaced ONLY with dit:greatCms
        'dit:greatCms:Article': 'Article',
        'dit:greatCms:Service': 'Service',
    }
    for value, replacement in mappings.items():
        if value in result['type']:
            result['type'] = replacement


def parse_search_results(content):

    results = [hit['_source'] for hit in content['hits']['hits']]

    # Clean any markup in the search results
    for result in results:
        _strip_html(result)
        _format_display_type(result)
        _abridge_long_contents(result)

    return results
