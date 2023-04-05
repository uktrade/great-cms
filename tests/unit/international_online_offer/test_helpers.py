from international_online_offer.core import helpers


def test_find_get_to_know_market_articles():
    assert helpers.find_get_to_know_market_articles([], '', []) == []


def test_concat_filters():
    assert helpers.concat_filters('test', ['test']) == ['test', 'test']
