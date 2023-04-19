from international_online_offer.core import scorecard


def test_is_levelling_up():
    assert not scorecard.is_levelling_up('London')
    assert scorecard.is_levelling_up('Wales')


def test_is_capex_spend():
    assert not scorecard.is_capex_spend('Food and Drink', '10000-500000')
    assert not scorecard.is_capex_spend('Food and Drink', '500001-1000000')
    assert scorecard.is_capex_spend('Food and Drink', '1000001-2000000')
    assert not scorecard.is_capex_spend('Random sector', '1000001-2000000')
    assert scorecard.is_capex_spend('Food and Drink', '10000000+')
    assert not scorecard.is_capex_spend('Food and Drink', 'Specific amount', '1234567')
    assert scorecard.is_capex_spend('Food and Drink', 'Specific amount', '12345678')
    assert not scorecard.is_capex_spend('Technology and Smart Cities', '0-10')
    assert scorecard.is_capex_spend('Technology and Smart Cities', '1000001-3000000')
    assert scorecard.is_capex_spend('Technology and Smart Cities', '10000000+')
    assert scorecard.is_capex_spend('Technology and Smart Cities', 'Specific amount', '2400000')


def test_is_labour_workforce_hire():
    assert not scorecard.is_labour_workforce_hire('Food and Drink', '1-10')
    assert scorecard.is_labour_workforce_hire('Food and Drink', '11-50')
    assert scorecard.is_labour_workforce_hire('Food and Drink', '101+')
    assert not scorecard.is_labour_workforce_hire('Random sector', '11-50')
    assert not scorecard.is_labour_workforce_hire('Food and Drink', 'No plans to hire yet')


def test_is_hpo():
    assert scorecard.is_hpo('Food and Drink', 'East')
    assert scorecard.is_hpo('Technology and Smart Cities', 'Wales')
    assert not scorecard.is_hpo('Food and Drink', 'Wales')
    assert not scorecard.is_hpo('Technology and Smart Cities', 'North East')


def test_score_is_high_value():
    assert not scorecard.score_is_high_value(None, None, None, None)
    assert not scorecard.score_is_high_value('Food and Drink', None, None, None)
    assert not scorecard.score_is_high_value('Food and Drink', 'London', None, None)
    assert scorecard.score_is_high_value('Food and Drink', 'Wales', None, None)
    assert not scorecard.score_is_high_value('Food and Drink', 'London', '1-10', None)
    assert scorecard.score_is_high_value('Food and Drink', 'London', '101+', None)
    assert not scorecard.score_is_high_value('Food and Drink', 'London', '1-10', '10000-500000')
    assert scorecard.score_is_high_value('Food and Drink', 'London', '1-10', '1000001-3000000')
    assert not scorecard.score_is_high_value('Food and Drink', 'London', '1-10', '10000-500000')
    assert scorecard.score_is_high_value('Food and Drink', 'London', '1-10', '1000001-3000000')
    assert not scorecard.score_is_high_value('Food and Drink', 'London', '1-10', 'Specific amount', '123')
    assert scorecard.score_is_high_value('Food and Drink', 'London', '1-10', 'Specific amount', '999999999')
