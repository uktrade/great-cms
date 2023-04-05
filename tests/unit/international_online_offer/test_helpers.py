from international_online_offer.core import helpers


def test_find_get_to_know_market_articles():
    tag = type(
        'obj',
        (object,),
        {'name': 'tag1'},
    )
    tag2 = type(
        'obj',
        (object,),
        {'name': 'tag2'},
    )
    specific = type(
        'obj',
        (object,),
        {'tags': [tag, tag2]},
    )
    article = type(
        'obj',
        (object,),
        {'specific': specific},
    )

    article2 = type(
        'obj',
        (object,),
        {'specific': specific},
    )

    articles = []
    articles.append(article)
    articles.append(article2)
    assert len(helpers.find_get_to_know_market_articles(articles, 'tag1', ['tag2'])) == 2
    assert helpers.find_get_to_know_market_articles([], '', []) == []


def test_concat_filters():
    assert helpers.concat_filters('test', ['test']) == ['test', 'test']
