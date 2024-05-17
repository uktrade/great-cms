import pytest

from directory_constants import sectors as directory_constants_sectors
from international_online_offer.core import hirings, regions, scorecard, sectors, spends
from international_online_offer.models import ScorecardCriterion


def populate_scoring_criteria():
    ScorecardCriterion.objects.create(
        sector=directory_constants_sectors.FOOD_AND_DRINK,
        capex_spend=None,
        labour_workforce_hire=20,
        high_potential_opportunity_locations=[regions.NORTH_EAST, regions.NORTH_WEST, regions.EAST_OF_ENGLAND],
    )
    ScorecardCriterion.objects.create(
        sector=sectors.TECHNOLOGY_AND_SMART_CITIES,
        capex_spend=None,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=[
            regions.WALES,
            regions.SOUTH_WEST,
            regions.EAST_OF_ENGLAND,
            regions.WEST_MIDLANDS,
            regions.YORKSHIRE_AND_THE_HUMBER,
        ],
    )
    ScorecardCriterion.objects.create(
        sector='Technology and smart cities : Communications',
        capex_spend=1079999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=None,
    )
    ScorecardCriterion.objects.create(
        sector='Technology and smart cities : Hardware',
        capex_spend=2399999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=None,
    )
    ScorecardCriterion.objects.create(
        sector='Energy : Civil nuclear',
        capex_spend=759999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=None,
    )
    ScorecardCriterion.objects.create(
        sector='Energy : Oil and gas',
        capex_spend=2219999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=None,
    )
    ScorecardCriterion.objects.create(
        sector='Financial and professional services : Business and consumer services',
        capex_spend=None,
        labour_workforce_hire=14,
        high_potential_opportunity_locations=None,
    )
    ScorecardCriterion.objects.create(
        sector=directory_constants_sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES,
        capex_spend=None,
        labour_workforce_hire=13,
        high_potential_opportunity_locations=None,
    )
    ScorecardCriterion.objects.create(
        sector=sectors.CREATIVE_INDUSTRIES,
        capex_spend=505999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=[regions.NORTH_EAST, regions.WEST_MIDLANDS, regions.SOUTH_EAST],
    )
    ScorecardCriterion.objects.create(
        sector=sectors.PHARMACEUTICALS_AND_BIOTECHNOLOGY,
        capex_spend=3191999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=[
            regions.NORTH_EAST,
            regions.SCOTLAND,
            regions.YORKSHIRE_AND_THE_HUMBER,
            regions.EAST_MIDLANDS,
            regions.NORTH_WEST,
            regions.EAST_OF_ENGLAND,
            regions.WALES,
            regions.NORTHERN_IRELAND,
        ],
    )
    ScorecardCriterion.objects.create(
        sector=sectors.HEALTHCARE_SERVICES,
        capex_spend=None,
        labour_workforce_hire=15,
        high_potential_opportunity_locations=[
            regions.NORTH_EAST,
            regions.SOUTH_EAST,
            regions.YORKSHIRE_AND_THE_HUMBER,
            regions.WEST_MIDLANDS,
        ],
    )
    ScorecardCriterion.objects.create(
        sector=directory_constants_sectors.ENERGY,
        capex_spend=3099999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=[regions.NORTH_EAST, regions.SCOTLAND, regions.SOUTH_EAST],
    )


@pytest.mark.django_db
def test_is_capex_spend():
    populate_scoring_criteria()
    assert not scorecard.is_capex_spend(
        directory_constants_sectors.FOOD_AND_DRINK,
        'Food and drink: cookies',
        spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND,
    )
    assert not scorecard.is_capex_spend(
        sectors.TECHNOLOGY_AND_SMART_CITIES,
        'Technology and smart cities : random sub sector',
        spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND,
    )
    assert not scorecard.is_capex_spend(
        sectors.TECHNOLOGY_AND_SMART_CITIES,
        'Technology and smart cities : random sub sector',
        spends.TWO_MILLION_TO_FIVE_MILLION,
    )
    assert scorecard.is_capex_spend(
        sectors.TECHNOLOGY_AND_SMART_CITIES,
        'Technology and smart cities : Communications',
        spends.ONE_MILLION_TO_TWO_MILLION,
    )
    assert not scorecard.is_capex_spend(
        sectors.TECHNOLOGY_AND_SMART_CITIES,
        'Technology and smart cities : Hardware',
        spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND,
    )
    assert scorecard.is_capex_spend(
        sectors.TECHNOLOGY_AND_SMART_CITIES,
        'Technology and smart cities : Hardware',
        spends.TWO_MILLION_TO_FIVE_MILLION,
    )
    assert not scorecard.is_capex_spend(
        directory_constants_sectors.ENERGY, 'Energy : Civil nuclear', spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND
    )
    assert scorecard.is_capex_spend(
        directory_constants_sectors.ENERGY, 'Energy : Civil nuclear', spends.ONE_MILLION_TO_TWO_MILLION
    )
    assert not scorecard.is_capex_spend(
        directory_constants_sectors.ENERGY, 'Energy : Oil and gas', spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND
    )
    assert scorecard.is_capex_spend(
        directory_constants_sectors.ENERGY, 'Energy : Oil and gas', spends.TWO_MILLION_TO_FIVE_MILLION
    )
    assert not scorecard.is_capex_spend(
        directory_constants_sectors.ENERGY, 'Energy: random sub sector', spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND
    )
    assert scorecard.is_capex_spend(
        directory_constants_sectors.ENERGY, 'Energy: random sub sector', spends.TWO_MILLION_TO_FIVE_MILLION
    )


@pytest.mark.django_db
def test_is_labour_workforce_hire():
    assert not scorecard.is_labour_workforce_hire(directory_constants_sectors.FOOD_AND_DRINK, '', hirings.ONE_TO_TEN)
    assert scorecard.is_labour_workforce_hire(directory_constants_sectors.FOOD_AND_DRINK, '', hirings.ELEVEN_TO_FIFTY)
    assert scorecard.is_labour_workforce_hire(
        directory_constants_sectors.FOOD_AND_DRINK, '', hirings.ONE_HUNDRED_ONE_PLUS
    )
    assert not scorecard.is_labour_workforce_hire('Random sector', '', hirings.ELEVEN_TO_FIFTY)
    assert not scorecard.is_labour_workforce_hire(
        directory_constants_sectors.FOOD_AND_DRINK, '', hirings.NO_PLANS_TO_HIRE_YET
    )
    assert not scorecard.is_labour_workforce_hire(
        directory_constants_sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES, '', hirings.ONE_TO_TEN
    )
    assert not scorecard.is_labour_workforce_hire(
        directory_constants_sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES,
        'Financial and professional services : Business and consumer services',
        hirings.ONE_TO_TEN,
    )
    assert scorecard.is_labour_workforce_hire(
        directory_constants_sectors.FINANCIAL_AND_PROFESSIONAL_SERVICES,
        'Financial and professional services : Business and consumer services',
        hirings.ELEVEN_TO_FIFTY,
    )


@pytest.mark.parametrize(
    'sector,region,expected_result',
    (
        (directory_constants_sectors.FOOD_AND_DRINK, regions.WALES, False),
        (directory_constants_sectors.FOOD_AND_DRINK, regions.EAST_OF_ENGLAND, True),
        (sectors.TECHNOLOGY_AND_SMART_CITIES, regions.NORTH_EAST, False),
        (sectors.TECHNOLOGY_AND_SMART_CITIES, regions.WALES, True),
        (sectors.CREATIVE_INDUSTRIES, regions.WALES, False),
        (sectors.CREATIVE_INDUSTRIES, regions.NORTH_EAST, True),
        (directory_constants_sectors.ENERGY, regions.WALES, False),
        (directory_constants_sectors.ENERGY, regions.SCOTLAND, True),
        (sectors.PHARMACEUTICALS_AND_BIOTECHNOLOGY, regions.LONDON, False),
        (sectors.PHARMACEUTICALS_AND_BIOTECHNOLOGY, regions.WALES, True),
        (sectors.HEALTHCARE_SERVICES, regions.SCOTLAND, False),
        (sectors.HEALTHCARE_SERVICES, regions.WEST_MIDLANDS, True),
    ),
)
@pytest.mark.django_db
def test_is_hpo(sector, region, expected_result):
    populate_scoring_criteria()
    assert scorecard.is_hpo(sector, region) == expected_result


@pytest.mark.django_db
def test_score_is_high_value():
    populate_scoring_criteria()
    assert not scorecard.score_is_high_value(None, None, None, None, None)
    assert not scorecard.score_is_high_value(directory_constants_sectors.FOOD_AND_DRINK, '', None, None, None)
    assert not scorecard.score_is_high_value(
        directory_constants_sectors.FOOD_AND_DRINK, '', regions.LONDON, hirings.ONE_TO_TEN, None
    )
    assert scorecard.score_is_high_value(
        directory_constants_sectors.FOOD_AND_DRINK, '', regions.LONDON, hirings.ONE_HUNDRED_ONE_PLUS, None
    )
    assert not scorecard.score_is_high_value(
        directory_constants_sectors.FOOD_AND_DRINK, '', regions.LONDON, hirings.ONE_TO_TEN, '1000001-3000000'
    )
