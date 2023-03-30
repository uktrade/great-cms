from international_online_offer.core import helpers


def test_find_get_to_know_market_articles():
    assert helpers.find_get_to_know_market_articles([], '', []) == []
