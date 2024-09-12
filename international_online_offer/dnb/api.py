import logging

from requests.exceptions import HTTPError

from .client import api_request
from .mapping import extract_company_data

logger = logging.getLogger(__name__)

DNB_COMPANY_SEARCH_ENDPOINT = '/v1/search/companyList'


def company_list_search(query: dict):
    try:
        response = api_request('POST', DNB_COMPANY_SEARCH_ENDPOINT, json=query)
    except HTTPError as ex:
        if ex.response.status_code == 404:
            response_data = {}
        else:
            raise
    else:
        response_data = response.json()

    results = [extract_company_data(item) for item in response_data.get('searchCandidates', [])]

    return {
        'total_matches': response_data.get('candidatesMatchedQuantity', 0),
        'total_returned': response_data.get('candidatesReturnedQuantity', 0),
        'page_size': response_data.get('inquiryDetail', {}).get('pageSize', 0),
        'page_number': response_data.get('inquiryDetail', {}).get('pageNumber', 1),
        'results': results,
    }
