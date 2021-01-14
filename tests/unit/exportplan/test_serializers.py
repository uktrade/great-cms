from collections import OrderedDict

import pytest

from exportplan import serializers


def test_about_your_business_serializer():

    data = {
        'story': 'Lorem ipsum',
        'location': 'Consectetur adipisicing elit',
        'packaging': 'Dolor sit amet',
        'processes': 'Sed do eiusmod tempor incididunt',
    }

    serializer = serializers.AboutYourBuinessSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_about_your_business_serializer_allows_blank_omitted():

    data = {
        'story': '',
        'location': '',
    }

    serializer = serializers.AboutYourBuinessSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_export_plan_serializer_empty_target_markets():

    data = {'about_your_business': {'story': '', 'location': ''}}

    serializer = serializers.ExportPlanSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_objective_serializer():

    data = {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': '2020-03-01',
        'end_date': '2020-12-23',
        'companyexportplan': 1,
        'pk': 2,
    }

    serializer = serializers.CompanyObjectiveSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_objective_serializer_empty_date_fields():

    data = {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': '',
        'end_date': '',
        'companyexportplan': 1,
    }

    serializer = serializers.NewObjectiveSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': None,
        'end_date': None,
        'companyexportplan': 1,
    }


def test_new_objective_serializer():

    data = {
        'description': 'Lorem ipsum',
        'planned_reviews': 'Some reviews',
        'owner': 'John Smith',
        'start_date': '2020-03-01',
        'end_date': '2020-12-23',
        'companyexportplan': 1,
    }

    serializer = serializers.NewObjectiveSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_pk_only_serializer():

    data = {'pk': 1}

    serializer = serializers.PkOnlySerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def target_markets_research_serializer():

    data = {
        'demand': 'Lorem ipsum',
        'competitors': 'Consectetur adipisicing elit',
        'trend': 'Dolor sit amet',
        'unqiue_selling_proposition': 'Sed do eiusmod tempor incididunt',
        'average_price': 10,
    }

    serializer = serializers.TargetMarketsResearchSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_country_target_age_serializer():
    data = {
        'country': 'uk',
        'target_age_groups': ['0-5,5-25'],
        'section_name': 'test-section',
    }
    serializer = serializers.CountryTargetAgeDataSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.data['target_age_groups'] == ['0-5', '5-25']


def test_country_target_age_serializer_missing_target_age():

    data = {'country': 'uk', 'target_age_groups': ''}
    serializer = serializers.CountryTargetAgeDataSerializer(data=data)
    assert serializer.is_valid() is False


def test_adaptation_target_market_serializer():

    data = {
        'labelling': 'Lorem ipsum',
        'packaging': 'Consectetur adipisicing elit',
        'size': 'Dolor sit amet',
        'standards': 'Sed do eiusmod tempor incididunt',
        'translations': 'In french',
        'other_changes': 'none',
        'certificate_of_origin': 'France',
        'insurance_certificate': '5',
        'commercial_invoice': 'XYZ_invoice',
        'uk_customs_declaration': 'not required',
    }

    serializer = serializers.AdaptationTargetMarketSerializer(data=data)

    assert serializer.is_valid()
    assert serializer.data == data


def test_objectives_serializer():

    data = {'rationale': 'test'}

    serializer = serializers.ObjectiveSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.data == data


def test_json_script_exploit():
    script_exploit = '<script>alert("CGI \\ \\XSS")</script><svg/onload=alert(document.cookie)>'
    data = {'story': script_exploit}

    serializer = serializers.AboutYourBuinessSerializer(data=data)
    assert serializer.is_valid() is False


def test_cost_and_pricing_serializers():
    data = {
        'direct_costs': {
            'product_costs': 12.02,
            'labour_costs': 13.02,
        },
        'overhead_costs': {
            'product_adaption': 13.02,
            'other_overhead_costs': 19.23,
        },
        'total_cost_and_price': {
            'units_to_export_first_period': {'unit': 'kg', 'value': 10.00},
            'average_price_per_unit': 23.44,
            'duty_per_unit': 23,
            'gross_price_per_unit_invoicing_currency': {'value': 23.4, 'unit': 'EUR'},
        },
    }

    serializer = serializers.ExportPlanSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.data['direct_costs'] == OrderedDict(
        {'product_costs': '12.02', 'labour_costs': '13.02'},
    )
    assert serializer.data['overhead_costs'] == OrderedDict(
        {'product_adaption': '13.02', 'other_overhead_costs': '19.23'},
    )
    assert serializer.data['total_cost_and_price'] == OrderedDict(
        {
            'units_to_export_first_period': OrderedDict(
                {'unit': 'kg', 'value': '10.00'},
            ),
            'average_price_per_unit': '23.44',
            'duty_per_unit': '23.00',
            'gross_price_per_unit_invoicing_currency': OrderedDict(
                {'unit': 'EUR', 'value': '23.40'},
            ),
        },
    )


def test_total_cost_direct_costs_serializer():
    data = {
        'product_costs': 12.02,
        'labour_costs': 13.02,
    }
    serializer = serializers.DirectCostsSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.calculate_total_direct_costs() == 25.04


def test_total_over_head_costs_serializer():
    data = {'product_adaption': '13.02', 'other_overhead_costs': '19.23'}
    serializer = serializers.OverheadCostsSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.calculate_total_overhead_costs() == 32.25


@pytest.mark.parametrize(
    'data, expected_profit_per_unit, expected_total_profit, expected_gross_unit_per_unit',
    [
        [
            {'final_cost_per_unit': 16.00, 'net_price': 22.00, 'units_to_export_first_period': {'value': 22.00}},
            6,
            132,
            0,
        ],
        [
            {'final_cost_per_unit': '16.00', 'net_price': '22.00', 'units_to_export_first_period': {'value': '22.00'}},
            6,
            132,
            0,
        ],
        [{'duty_per_unit': 0.50, 'net_price': 22.00}, 0, 0, 11],
    ],
)
def test_total_cost_and_price_serializer(
    data, expected_profit_per_unit, expected_total_profit, expected_gross_unit_per_unit
):
    serializer = serializers.TotalCostAndPriceSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.calculate_profit_per_unit() == expected_profit_per_unit
    assert serializer.calculate_potential_total_profit() == expected_total_profit
    assert serializer.calculate_gross_price_per_unit() == expected_gross_unit_per_unit


@pytest.mark.parametrize(
    'pricing_data, expected',
    [
        [
            {'total_cost_and_price': {'final_cost_per_unit': 16.00, 'net_price': 22.00}},
            {'profit_per_unit': 6.0, 'potential_total_profit': 0.0, 'gross_price_per_unit': 0},
        ],
        [
            {
                'total_cost_and_price': {
                    'final_cost_per_unit': 16.00,
                    'net_price': 22.00,
                    'units_to_export_first_period': {'value': 22.00},
                }
            },
            {'profit_per_unit': 6.0, 'potential_total_profit': 132.00, 'gross_price_per_unit': 0},
        ],
        [
            {'total_cost_and_price': {'net_price': 6.0, 'duty_per_unit': 0.5}},
            {'profit_per_unit': 0.0, 'potential_total_profit': 0.0, 'gross_price_per_unit': 3.0},
        ],
        [
            {'total_cost_and_price': {'final_cost_per_unit': 22.0}},
            {'profit_per_unit': 0.0, 'potential_total_profit': 0.0, 'gross_price_per_unit': 0.0},
        ],
        [{'total_cost_and_price': {}}, {}],
        [
            {'direct_costs': {'product_costs': 10.00, 'labour_costs': 5.00, 'other_direct_costs': 2.00}},
            {'total_direct_costs': 17},
        ],
        [{'direct_costs': {'product_costs': 10.00, 'labour_costs': 5.00}}, {'total_direct_costs': 15}],
        [{'overhead_costs': {'insurance': 10.00, 'marketing': 1345.00}}, {'total_overhead_costs': 1355.00}],
        [{}, {}],
    ],
)
def test_exportplan_serializer_calculate_cost_pricing(pricing_data, expected):
    serializer = serializers.ExportPlanSerializer(data=pricing_data)
    assert serializer.calculate_cost_pricing() == expected
