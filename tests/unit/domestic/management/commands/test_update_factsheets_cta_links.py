from io import StringIO

import pytest
from django.core.management import call_command

from tests.unit.domestic.factories import CountryGuidePageFactory

CONTENT_API_LANDING_RESPONSE = {
    'links': {
        'documents': [
            {
                'document_type': 'official_statistics',
                'api_url': 'https://www.gov.uk/api/factsheets-a-to-l',
            },
            {'document_type': 'official_statistics', 'api_url': 'https://www.gov.uk/api/factsheets-m-to-z'},
            {'document_type': 'research', 'api_url': 'https://www.gov.uk/api/methodology-report'},
        ]
    }
}
CONTENT_API_A_TO_L_RESPONSE = {
    'details': {
        'attachments': [
            {
                'url': 'https://assets.publishing.service.gov.uk/123/afghanistan-factsheet-2022-02-18.pdf',
                'title': 'Trade and investment factsheets: Afghanistan',
            },
            {
                'url': 'https://assets.publishing.service.gov.uk/124/antigua-and-barbuda-factsheet-2022-02-18.pdf',
                'title': 'Trade and investment factsheets: Antigua and Barbuda',
            },
            {
                'url': 'https://assets.publishing.service.gov.uk/130/hong-kong-sar-factsheet-2022-02-18.pdf',
                'title': 'Trade and investment factsheets: Hong Kong, SAR',
            },
            {
                'url': 'https://assets.publishing.service.gov.uk/126/ivory-coast-factsheet-2022-02-18.pdf',
                'title': 'Trade and investment factsheets: Ivory Coast',
            },
            {
                'url': 'https://assets.publishing.service.gov.uk/127'
                '/british-indian-ocean-territory-factsheet-2022-02-18.pdf',
                'title': 'Trade and investment factsheets: British Indian Ocean Territory',
            },
            {
                'url': 'https://assets.publishing.service.gov.uk/128/india-factsheet-2022-02-18.pdf',
                'title': 'Trade and investment factsheets: India',
            },
        ]
    }
}
CONTENT_API_M_TO_Z_RESPONSE = {
    'details': {
        'attachments': [
            {
                'url': 'https://assets.publishing.service.gov.uk/129/netherlands-factsheet-2022-02-18.pdf',
                'title': 'Trade and investment factsheets: Netherlands',
            },
            {
                'url': 'https://assets.publishing.service.gov.uk/125/united-states-factsheet-2022-02-18.pdf',
                'title': 'Trade and investment factsheets: United States',
            },
        ]
    }
}


@pytest.mark.parametrize(
    'data, expected',
    (
        (
            {'title': 'Antigua and Barbuda', 'intro_cta_three_link': 'http://original-link'},
            'https://assets.publishing.service.gov.uk/124/antigua-and-barbuda-factsheet-2022-02-18.pdf',
        ),
        (
            {'title': 'United States (US)', 'intro_cta_three_link': 'http://original-link'},
            'https://assets.publishing.service.gov.uk/125/united-states-factsheet-2022-02-18.pdf',
        ),
        (
            {'title': 'Ivory Coast  (The Republic of Côte D’Ivoire)', 'intro_cta_three_link': 'http://original-link'},
            'https://assets.publishing.service.gov.uk/126/ivory-coast-factsheet-2022-02-18.pdf',
        ),
        ({'title': 'Will not be found', 'intro_cta_three_link': 'http://original-link'}, 'http://original-link'),
        (
            {'title': 'India', 'intro_cta_three_link': 'http://original-link'},
            'https://assets.publishing.service.gov.uk/128/india-factsheet-2022-02-18.pdf',
        ),
        (
            {'title': 'The Netherlands', 'intro_cta_three_link': 'http://original-link'},
            'https://assets.publishing.service.gov.uk/129/netherlands-factsheet-2022-02-18.pdf',
        ),
        (
            {'title': 'Hong Kong, China', 'intro_cta_three_link': 'http://original-link'},
            'https://assets.publishing.service.gov.uk/130/hong-kong-sar-factsheet-2022-02-18.pdf',
        ),
    ),
)
@pytest.mark.django_db
def test_update_factsheets_cta_links(data, expected, domestic_homepage, requests_mock):
    requests_mock.get(
        'https://www.gov.uk/api/content/government/collections/trade-and-investment-factsheets',
        json=CONTENT_API_LANDING_RESPONSE,
    )
    requests_mock.get('https://www.gov.uk/api/factsheets-a-to-l', json=CONTENT_API_A_TO_L_RESPONSE)
    requests_mock.get('https://www.gov.uk/api/factsheets-m-to-z', json=CONTENT_API_M_TO_Z_RESPONSE)

    guide = CountryGuidePageFactory(parent=domestic_homepage, **data)
    guide.save()

    call_command('update_factsheets_cta_links', stdout=StringIO())

    guide.refresh_from_db()

    assert guide.intro_cta_three_link == expected
