import pytest

from domestic import serializers
from tests.unit.core.factories import CountryFactory, IndustryTagFactory
from tests.unit.domestic.factories import CountryGuidePageFactory


@pytest.mark.django_db
def test_market_guides_map_serializer(domestic_homepage):
    country = CountryFactory(
        name='France',
        iso2='FR',
        latlng='51.4,-3.5',
    )
    tag_1 = IndustryTagFactory(name='Automotive')
    tag_2 = IndustryTagFactory(name='Aerospace')
    guide = CountryGuidePageFactory(
        parent=domestic_homepage, heading='France market guide', country=country, slug='france', tags=[tag_1, tag_2]
    )
    serialized = serializers.MarketGuidesMapSerializer().serialize([guide])

    assert serialized[0]['heading'] == 'France market guide'
    assert serialized[0]['latlng'] == '51.4,-3.5'
    assert serialized[0]['url'] == '/markets/france/'
    assert serialized[0]['tags'] == ['Aerospace', 'Automotive']
