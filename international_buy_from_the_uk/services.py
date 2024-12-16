from directory_components.helpers import CompanyParser
from django.utils.html import escape, mark_safe

from directory_api_client.client import api_client
from directory_constants.choices import INDUSTRIES

INDUSTRY_CHOICES = dict(INDUSTRIES)


class CompanyParser(CompanyParser):
    def serialize_for_template(self):
        if not self.data:
            return {}
        return {
            **self.data,
            'date_of_creation': self.date_of_creation,
            'address': self.address,
            'sectors': self.sectors_label,
            'keywords': self.keywords,
            'employees': self.employees_label,
            'expertise_industries': self.expertise_industries_label,
            'expertise_regions': self.expertise_regions_label,
            'expertise_countries': self.expertise_countries_label,
            'expertise_languages': self.expertise_languages_label,
            'has_expertise': self.has_expertise,
            'expertise_products_services': (self.expertise_products_services_label),
            'is_in_companies_house': self.is_in_companies_house,
        }


def get_company_profile(number):
    response = api_client.company.published_profile_retrieve(number=number)
    response.raise_for_status()
    return get_company_from_response(response)


def get_company_from_response(response):
    parser = CompanyParser(response.json())
    return parser.serialize_for_template()


def search_companies(query, industries, page=1, page_size=10):
    response = api_client.company.search_find_a_supplier(
        term=query,
        sectors=industries,
        page=page,
        size=page_size,
    )
    response.raise_for_status()
    formatted = get_results_from_search_response(response)
    return formatted['results'], formatted['hits']['total']['value']


def get_results_from_search_response(response):
    parsed = response.json()
    formatted_results = []

    for result in parsed['hits']['hits']:
        parser = CompanyParser(result['_source'])
        formatted = parser.serialize_for_template()
        if 'highlight' in result:
            highlighted = '...'.join(
                result['highlight'].get('description', '') or result['highlight'].get('summary', '')
            )
            # escape all html tags other than <em> and </em>
            highlighted_escaped = escape(highlighted).replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')
            formatted['highlight'] = mark_safe(highlighted_escaped)
        formatted_results.append(formatted)

    parsed['results'] = formatted_results
    return parsed


def get_case_study(case_study_id):
    response = api_client.company.published_case_study_retrieve(case_study_id=case_study_id)
    response.raise_for_status()
    return get_case_study_from_response(response)


def get_case_study_from_response(response):
    case_study = response.json()
    # `format_company_details` expects `supplier_case_studies` key.
    case_study['company']['supplier_case_studies'] = []
    case_study['sector'] = pair_sector_value_with_label(case_study['sector'])
    case_study['company'] = CompanyParser(case_study['company']).serialize_for_template()
    return case_study


def pair_sector_value_with_label(sectors_value):
    return {'value': sectors_value, 'label': get_sectors_label(sectors_value)}


def get_sectors_label(sectors_value):
    if not sectors_value:
        return sectors_value
    return INDUSTRY_CHOICES.get(sectors_value)
