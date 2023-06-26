from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import hirings, regions, scorecard, sectors, spends


def test_is_capex_spend():
    assert not scorecard.is_capex_spend(
        directory_constants_sectors.FOOD_AND_DRINK, spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND
    )
    assert not scorecard.is_capex_spend(
        directory_constants_sectors.FOOD_AND_DRINK, spends.FIVE_HUNDRED_THOUSAND_ONE_TO_ONE_MILLION
    )
    assert scorecard.is_capex_spend(directory_constants_sectors.FOOD_AND_DRINK, spends.ONE_MILLION_ONE_TO_TWO_MILLION)
    assert not scorecard.is_capex_spend('Random sector', spends.ONE_MILLION_ONE_TO_TWO_MILLION)
    assert scorecard.is_capex_spend(directory_constants_sectors.FOOD_AND_DRINK, spends.TEN_MILLION_ONE_PLUS)
    assert not scorecard.is_capex_spend(directory_constants_sectors.FOOD_AND_DRINK, spends.SPECIFIC_AMOUNT, '1234567')
    assert scorecard.is_capex_spend(directory_constants_sectors.FOOD_AND_DRINK, spends.SPECIFIC_AMOUNT, '12345678')
    assert not scorecard.is_capex_spend(sectors.TECHNOLOGY_AND_SMART_CITIES, '0-10')
    assert scorecard.is_capex_spend(sectors.TECHNOLOGY_AND_SMART_CITIES, '1000001-3000000')
    assert scorecard.is_capex_spend(sectors.TECHNOLOGY_AND_SMART_CITIES, spends.TEN_MILLION_ONE_PLUS)
    assert scorecard.is_capex_spend(sectors.TECHNOLOGY_AND_SMART_CITIES, spends.SPECIFIC_AMOUNT, '2400000')


def test_is_labour_workforce_hire():
    assert not scorecard.is_labour_workforce_hire(directory_constants_sectors.FOOD_AND_DRINK, hirings.ONE_TO_TEN)
    assert scorecard.is_labour_workforce_hire(directory_constants_sectors.FOOD_AND_DRINK, hirings.ELEVEN_TO_FIFTY)
    assert scorecard.is_labour_workforce_hire(directory_constants_sectors.FOOD_AND_DRINK, hirings.ONE_HUNDRED_ONE_PLUS)
    assert not scorecard.is_labour_workforce_hire('Random sector', hirings.ELEVEN_TO_FIFTY)
    assert not scorecard.is_labour_workforce_hire(
        directory_constants_sectors.FOOD_AND_DRINK, hirings.NO_PLANS_TO_HIRE_YET
    )


def test_is_hpo():
    assert scorecard.is_hpo(directory_constants_sectors.FOOD_AND_DRINK, regions.EASTERN)
    assert scorecard.is_hpo(sectors.TECHNOLOGY_AND_SMART_CITIES, regions.WALES)
    assert not scorecard.is_hpo(directory_constants_sectors.FOOD_AND_DRINK, regions.WALES)
    assert not scorecard.is_hpo(sectors.TECHNOLOGY_AND_SMART_CITIES, regions.NORTH_EAST)


def test_score_is_high_value():
    assert not scorecard.score_is_high_value(None, None, None, None)
    assert not scorecard.score_is_high_value(directory_constants_sectors.FOOD_AND_DRINK, None, None, None)
    assert not scorecard.score_is_high_value(
        directory_constants_sectors.FOOD_AND_DRINK, regions.LONDON, hirings.ONE_TO_TEN, None
    )
    assert scorecard.score_is_high_value(
        directory_constants_sectors.FOOD_AND_DRINK, regions.LONDON, hirings.ONE_HUNDRED_ONE_PLUS, None
    )
    assert not scorecard.score_is_high_value(
        directory_constants_sectors.FOOD_AND_DRINK, regions.LONDON, hirings.ONE_TO_TEN, '1000001-3000000'
    )
    assert not scorecard.score_is_high_value(
        directory_constants_sectors.FOOD_AND_DRINK, regions.LONDON, hirings.ONE_TO_TEN, spends.SPECIFIC_AMOUNT, '99'
    )
    assert not scorecard.score_is_high_value(
        directory_constants_sectors.FOOD_AND_DRINK,
        regions.LONDON,
        hirings.ONE_TO_TEN,
        spends.SPECIFIC_AMOUNT,
        '999999999',
    )
