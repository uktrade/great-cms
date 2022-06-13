import pytest

from domestic import serializers
from tests.unit.core.factories import CountryFactory
from tests.unit.domestic.factories import CountryGuidePageFactory


@pytest.mark.django_db
def test_market_guides_map_serializer(domestic_homepage):
    country = CountryFactory(
        name='France',
        iso2='FR',
        latlng='51.4,-3.5',
    )
    guide = CountryGuidePageFactory(
        parent=domestic_homepage, heading='France market guide', country=country, slug='france'
    )
    serialized = serializers.MarketGuidesMapSerializer().serialize([guide])

    assert serialized[0]['heading'] == 'France market guide'
    assert serialized[0]['latlng'] == '51.4,-3.5'
    assert serialized[0]['url'] == '/markets/france/'
