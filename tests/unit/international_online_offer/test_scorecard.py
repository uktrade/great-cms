import pytest

from international_online_offer.core import hirings, regions, scorecard, spends
from international_online_offer.models import ScorecardCriterion


def populate_scoring_criteria():
    ScorecardCriterion.objects.create(
        sector='Food and drink',
        capex_spend=None,
        labour_workforce_hire=20,
        high_potential_opportunity_locations=[regions.NORTH_EAST, regions.NORTH_WEST, regions.EAST_OF_ENGLAND],
    )
    ScorecardCriterion.objects.create(
        sector='Technology and smart cities',
        capex_spend=2399999,
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
        sector='Financial and professional services',
        capex_spend=None,
        labour_workforce_hire=13,
        high_potential_opportunity_locations=None,
    )
    ScorecardCriterion.objects.create(
        sector='Creative industries',
        capex_spend=505999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=[regions.NORTH_EAST, regions.WEST_MIDLANDS, regions.SOUTH_EAST],
    )
    ScorecardCriterion.objects.create(
        sector='Pharmaceuticals and biotechnology',
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
        sector='Healthcare services',
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
        sector='Energy',
        capex_spend=3099999,
        labour_workforce_hire=None,
        high_potential_opportunity_locations=[regions.NORTH_EAST, regions.SCOTLAND, regions.SOUTH_EAST],
    )


@pytest.mark.django_db
def test_is_capex_spend():
    populate_scoring_criteria()
    assert not scorecard.is_capex_spend(
        'Food and drink',
        spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND,
    )
    assert not scorecard.is_capex_spend(
        'Technology and smart cities',
        spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND,
    )
    assert scorecard.is_capex_spend(
        'Technology and smart cities',
        spends.TWO_MILLION_TO_FIVE_MILLION,
    )
    assert not scorecard.is_capex_spend(
        'Technology and smart cities',
        spends.ONE_MILLION_TO_TWO_MILLION,
    )
    assert not scorecard.is_capex_spend(
        'Technology and smart cities',
        spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND,
    )
    assert scorecard.is_capex_spend(
        'Technology and smart cities',
        spends.TWO_MILLION_TO_FIVE_MILLION,
    )
    assert not scorecard.is_capex_spend('Energy', spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND)
    assert not scorecard.is_capex_spend('Energy', spends.ONE_MILLION_TO_TWO_MILLION)
    assert not scorecard.is_capex_spend('Energy', spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND)
    assert scorecard.is_capex_spend('Energy', spends.TWO_MILLION_TO_FIVE_MILLION)
    assert not scorecard.is_capex_spend('Energy', spends.TEN_THOUSAND_TO_FIVE_HUNDRED_THOUSAND)
    assert scorecard.is_capex_spend('Energy', spends.TWO_MILLION_TO_FIVE_MILLION)


@pytest.mark.django_db
def test_is_labour_workforce_hire():
    populate_scoring_criteria()
    assert not scorecard.is_labour_workforce_hire('Food and drink', hirings.ONE_TO_FIVE)
    assert scorecard.is_labour_workforce_hire('Food and drink', hirings.SIX_TO_FIFTY)
    assert scorecard.is_labour_workforce_hire('Food and drink', hirings.ONE_HUNDRED_ONE_PLUS)
    assert not scorecard.is_labour_workforce_hire('Random sector', hirings.SIX_TO_FIFTY)
    assert not scorecard.is_labour_workforce_hire('Food and drink', hirings.NO_PLANS_TO_HIRE_YET)
    assert not scorecard.is_labour_workforce_hire('Financial and professional services', hirings.ONE_TO_FIVE)
    assert not scorecard.is_labour_workforce_hire(
        'Financial and professional services',
        hirings.ONE_TO_FIVE,
    )
    assert scorecard.is_labour_workforce_hire(
        'Financial and professional services',
        hirings.SIX_TO_FIFTY,
    )


@pytest.mark.parametrize(
    'sector,region,expected_result',
    (
        ('Food and drink', regions.WALES, False),
        ('Food and drink', regions.EAST_OF_ENGLAND, True),
        ('Technology and smart cities', regions.NORTH_EAST, False),
        ('Technology and smart cities', regions.WALES, True),
        ('Creative industries', regions.WALES, False),
        ('Creative industries', regions.NORTH_EAST, True),
        ('Energy', regions.WALES, False),
        ('Energy', regions.SCOTLAND, True),
        ('Pharmaceuticals and biotechnology', regions.LONDON, False),
        ('Pharmaceuticals and biotechnology', regions.WALES, True),
        ('Healthcare services', regions.SCOTLAND, False),
        ('Healthcare services', regions.WEST_MIDLANDS, True),
    ),
)
@pytest.mark.django_db
def test_is_hpo(sector, region, expected_result):
    populate_scoring_criteria()
    assert scorecard.is_hpo(sector, region) == expected_result


@pytest.mark.django_db
def test_score_is_high_value():
    populate_scoring_criteria()
    assert not scorecard.score_is_high_value(None, None, None, None)
    assert not scorecard.score_is_high_value('Food and drink', None, None, None)
    assert not scorecard.score_is_high_value('Food and drink', regions.LONDON, hirings.ONE_TO_FIVE, None)
    assert scorecard.score_is_high_value('Food and drink', regions.LONDON, hirings.ONE_HUNDRED_ONE_PLUS, None)
    assert not scorecard.score_is_high_value('Food and drink', regions.LONDON, hirings.ONE_TO_FIVE, '1000001-3000000')
