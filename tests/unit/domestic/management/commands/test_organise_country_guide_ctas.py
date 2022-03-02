from io import StringIO

import pytest
from django.core.management import call_command

from tests.unit.core.factories import CountryFactory
from tests.unit.domestic.factories import CountryGuidePageFactory


@pytest.mark.django_db
def test_organise_ctas(domestic_homepage):
    ctas = {
        'intro_cta_one_title': 'View live export opportunities for Antigua and Barbuda',
        'intro_cta_one_link': 'https://www.great.gov.uk/export-opportunities/opportunities?s=&areas%5B%5D=antigua-and'
        '-barbuda&commit=Find+opportunities',
        'intro_cta_two_title': 'Find an online marketplace in Antigua and Barbuda',
        'intro_cta_two_link': 'https://www.great.gov.uk/selling-online-overseas/markets/results/?category_id'
        '=&country_id=344&commit=',
        'intro_cta_three_title': 'Find export events for Antigua and Barbuda',
        'intro_cta_three_link': 'https://www.events.great.gov.uk/ehome/index.php?eventid=200183029&',
        'intro_cta_four_title': '',
        'intro_cta_four_link': '',
    }

    country = CountryFactory(name='Antigua and Barbuda', slug='antigua-and-barbuda', iso2='AG')

    guide = CountryGuidePageFactory(
        parent=domestic_homepage,
        title='Test Country Guide for Antigua and Barbuda',
        heading='Antigua and Barbuda',
        country=country,
        **ctas,
    )
    guide.save()

    call_command('organise_country_guide_ctas', stdout=StringIO())

    guide.refresh_from_db()

    assert guide.intro_cta_one_title == 'View export opportunities'
    assert (
        guide.intro_cta_one_link == 'https://www.great.gov.uk/export-opportunities/opportunities?s=&areas%5B%5D'
        '=antigua-and-barbuda&commit=Find+opportunities'
    )
    assert guide.intro_cta_two_title == 'Find latest export events'
    assert (
        guide.intro_cta_two_link == 'https://www.events.great.gov.uk/ehome/trade-events-calendar/all-events'
        '/?keyword=Antigua%20and%20Barbuda'
    )
    assert guide.intro_cta_three_title == 'View latest trade statistics'
    assert (
        guide.intro_cta_three_link == 'https://www.gov.uk/government/statistics/trade-and-investment-factsheets'
        '-partner-names-beginning-with-a-or-b'
    )
    assert guide.intro_cta_four_title == 'Find an online marketplace'
    assert (
        guide.intro_cta_four_link == 'https://www.great.gov.uk/selling-online-overseas/markets/results'
        '/?category_id=&country_id=344&commit='
    )


@pytest.mark.django_db
def test_organise_ctas_custom_events_link(domestic_homepage):
    ctas = {
        'intro_cta_three_title': 'Find export events for Antigua and Barbuda',
        'intro_cta_three_link': 'https://example.org/events',
    }

    guide = CountryGuidePageFactory(
        parent=domestic_homepage,
        title='Test Country Guide for Antigua and Barbuda',
        heading='Antigua and Barbuda',
        **ctas,
    )

    guide.save()

    call_command('organise_country_guide_ctas', stdout=StringIO())

    guide.refresh_from_db()

    assert guide.intro_cta_one_title == ''
    assert guide.intro_cta_one_link == ''
    assert guide.intro_cta_two_title == 'Find latest export events'
    assert guide.intro_cta_two_link == 'https://example.org/events'
    assert guide.intro_cta_three_title == 'View latest trade statistics'
    assert (
        guide.intro_cta_three_link == 'https://www.gov.uk/government/statistics/trade-and-investment-factsheets'
        '-partner-names-beginning-with-a-or-b'
    )
    assert guide.intro_cta_four_title == ''
    assert guide.intro_cta_four_link == ''
