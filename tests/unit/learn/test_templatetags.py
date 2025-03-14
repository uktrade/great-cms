import pytest
from django.utils import timezone
from wagtail.models import Page
from wagtail_factories import PageChooserBlockFactory

from learn.templatetags.helpers import get_article_cta_attributes, get_cta_attributes
from tests.unit.export_academy.factories import EventFactory
from .factories import (
    EventOrderableFactory,
    RelatedContentCTASnippetFactory,
    UKEACTASnippetFactory,
)


@pytest.mark.parametrize(
    'link_text, type, url, expected',
    (
        (
            'GREAT service',
            'great_service',
            '/homepage/',
            {
                'link': '/',
                'tag_description': 'Service',
            },
        ),
        (
            'GREAT guidance',
            'great_guidance',
            '/homepage/',
            {
                'link': '/',
                'tag_description': 'Guidance',
            },
        ),
        (
            'GOV.UK service',
            'govuk_service',
            'https://www.gov.uk',
            {
                'link': 'https://www.gov.uk',
                'tag_description': 'Service on GOV.UK',
            },
        ),
        (
            'GOV.UK guidance',
            'govuk_guidance',
            'https://www.gov.uk',
            {
                'link': 'https://www.gov.uk',
                'tag_description': 'Guidance on GOV.UK',
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


@pytest.mark.parametrize(
    'name, events, expected',
    (
        (
            'test',
            None,
            {
                'image': '/static/images/ukea-landing.png',
                'icon': '/static/icons/hand.svg',
                'type': 'Service',
            },
        ),
        (
            'test',
            1,
            {
                'image': '/static/images/ukea-landing.png',
                'icon': '/static/icons/event-icon.jpeg',
                'type': 'Event',
            },
        ),
        (
            'test',
            2,
            {
                'image': '/static/images/ukea-landing.png',
                'icon': '/static/icons/event-icon.jpeg',
                'type': 'Event',
            },
        ),
    ),
)
@pytest.mark.django_db
def test_get_article_cta_attributes(root_page, name, events, expected):
    cta = UKEACTASnippetFactory(name=name)

    if events:
        for loop in range(events):
            delta = timezone.now() + timezone.timedelta(days=1 + loop)
            event_obj = EventFactory(start_date=delta, live=delta, completed=None)
            EventOrderableFactory(page=cta, event=event_obj)

    cta_attrs = get_article_cta_attributes(cta)

    assert cta_attrs['image'] == expected['image']
    assert cta_attrs['icon'] == expected['icon']
    assert cta_attrs['type'] == expected['type']
