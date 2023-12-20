import pytest
from wagtail.models import Page
from wagtail_factories import PageChooserBlockFactory

from learn.templatetags.helpers import get_cta_attributes
from .factories import RelatedContentCTASnippetFactory


@pytest.mark.parametrize(
    'link_text, type, url, expected',
    (
        (
            'GREAT service',
            'great_service',
            '/homepage/',
            {
                'link': '/',
                'heading_class': 'govuk-body-s ',
                'tag_description': 'Service',
                'tag_icon': '/static/icons/hand.svg',
            },
        ),
        (
            'GREAT guidance',
            'great_guidance',
            '/homepage/',
            {
                'link': '/',
                'heading_class': 'govuk-body-s ',
                'tag_description': 'Guidance',
                'tag_icon': '/static/icons/guidance.svg',
            },
        ),
        (
            'GOV.UK service',
            'govuk_service',
            'https://www.gov.uk',
            {
                'link': 'https://www.gov.uk',
                'heading_class': 'govuk-body-s great-card__link--external',
                'tag_description': 'Service on GOV.UK',
                'tag_icon': '/static/icons/hand.svg',
            },
        ),
        (
            'GOV.UK guidance',
            'govuk_guidance',
            'https://www.gov.uk',
            {
                'link': 'https://www.gov.uk',
                'heading_class': 'govuk-body-s great-card__link--external',
                'tag_description': 'Guidance on GOV.UK',
                'tag_icon': '/static/icons/guidance.svg',
            },
        ),
    ),
)
@pytest.mark.django_db
def test_get_cta_attributes(domestic_site, link_text, type, url, expected):
    if 'http' in url:
        link = [('link', url)]
    else:
        link = [('page', PageChooserBlockFactory(page=Page.objects.get(url_path=url)))]

    cta = RelatedContentCTASnippetFactory(link_text=link_text, type=type, link=link)

    cta_attrs = get_cta_attributes(cta)

    assert cta_attrs == expected
