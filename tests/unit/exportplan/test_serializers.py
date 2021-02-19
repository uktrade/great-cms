import json
from collections import OrderedDict
from datetime import datetime

import pytest
from freezegun import freeze_time

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
            'units_to_export_first_period': {'unit': 'kg', 'value': 10},
            'average_price_per_unit': 23.44,
            'duty_per_unit': 23,
            'gross_price_per_unit_invoicing_currency': {'value': 23.4, 'unit': 'EUR'},
        },
    }

    serializer = serializers.ExportPlanSerializer(data=data)
    assert serializer.is_valid()

    assert serializer.data['direct_costs'] == OrderedDict([('product_costs', '12.02'), ('labour_costs', '13.02')])

    assert serializer.data['overhead_costs'] == OrderedDict(
        [('product_adaption', '13.02'), ('other_overhead_costs', '19.23')]
    )
    assert serializer.data['total_cost_and_price'] == OrderedDict(
        [
            ('units_to_export_first_period', OrderedDict([('unit', 'kg'), ('value', 10)])),
            ('average_price_per_unit', '23.44'),
            ('duty_per_unit', '23.00'),
            ('gross_price_per_unit_invoicing_currency', OrderedDict([('unit', 'EUR'), ('value', '23.40')])),
        ]
    )


def test_total_cost_direct_costs_serializer():
    data = {
        'product_costs': 12.02,
        'labour_costs': 13.02,
    }
    serializer = serializers.DirectCostsSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.total_direct_costs == 25.04


def test_total_over_head_costs_serializer():
    data = {'product_adaption': '13.02', 'other_overhead_costs': '19.23'}
    serializer = serializers.OverheadCostsSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.total_overhead_costs == 32.25


@pytest.mark.parametrize(
    'data, expected_profit_per_unit, expected_total_profit, expected_gross_unit_per_unit',
    [
        [
            {'final_cost_per_unit': 16.00, 'net_price': 22.00, 'units_to_export_first_period': {'value': 22.00}},
            6.00,
            132.00,
            22.00,
        ],
        [
            {'final_cost_per_unit': '16.00', 'net_price': '22.00', 'units_to_export_first_period': {'value': '22.00'}},
            6.00,
            132.00,
            22.00,
        ],
        [{'duty_per_unit': 15, 'net_price': 22.00}, 0.00, 0.00, 37.00],
    ],
)
def test_total_cost_and_price_serializer(
    data, expected_profit_per_unit, expected_total_profit, expected_gross_unit_per_unit
):
    serializer = serializers.TotalCostAndPriceSerializer(data=data)
    assert serializer.is_valid()
    assert serializer.profit_per_unit == expected_profit_per_unit
    assert serializer.potential_total_profit == expected_total_profit
    assert serializer.gross_price_per_unit == expected_gross_unit_per_unit


def test_exportplan_serializer_calculate_cost_pricing(export_plan_data):
    serializer = serializers.ExportPlanSerializer(data=export_plan_data)
    assert serializer.calculate_cost_pricing == {
        'total_direct_costs': '15.00',
        'total_overhead_costs': '1355.00',
        'profit_per_unit': '6.00',
        'potential_total_profit': '132.00',
        'gross_price_per_unit': '42.36',
        'total_export_costs': '1685.00',
        'estimated_costs_per_unit': '76.59',
    }


def test_exportplan_serializer_calculate_cost_pricing_no_over_head_costs(export_plan_data):
    del export_plan_data['total_cost_and_price']
    serializer = serializers.ExportPlanSerializer(data=export_plan_data)
    assert serializer.calculate_cost_pricing == {
        'total_direct_costs': '15.00',
        'total_overhead_costs': '1355.00',
        'profit_per_unit': '0.00',
        'potential_total_profit': '0.00',
        'gross_price_per_unit': '0.00',
        'total_export_costs': '0.00',
        'estimated_costs_per_unit': '15.00',
    }


def test_total_direct_costs(cost_pricing_data):
    serializer = serializers.ExportPlanSerializer(data=cost_pricing_data)
    assert serializer.total_direct_costs == 15.00


def test_total_overhead_costs(cost_pricing_data):
    serializer = serializers.ExportPlanSerializer(data=cost_pricing_data)
    assert serializer.total_overhead_costs == 1355.00


def test_total_export_costs(cost_pricing_data):
    serializer = serializers.ExportPlanSerializer(data=cost_pricing_data)
    assert serializer.total_export_costs == 1685.00


def test_estimated_costs_per_unit(cost_pricing_data):
    serializer = serializers.ExportPlanSerializer(data=cost_pricing_data)
    assert serializer.estimated_costs_per_unit == 76.5909090909091


def test_json_to_presentaion(cost_pricing_data):
    json_data = serializers.ExportPlanSerializer().cost_and_pricing_to_json(cost_pricing_data)
    assert json_data == json.dumps(
        {
            'direct_costs': {'product_costs': '10.00', 'labour_costs': '5.00', 'other_direct_costs': ''},
            'overhead_costs': {
                'product_adaption': '',
                'freight_logistics': '',
                'agent_distributor_fees': '',
                'marketing': '1345.00',
                'insurance': '10.00',
                'other_overhead_costs': '',
            },
            'total_cost_and_price': {
                'units_to_export_first_period': {'unit': '', 'value': 22},
                'units_to_export_second_period': {'unit': '', 'value': ''},
                'final_cost_per_unit': '16.00',
                'average_price_per_unit': '',
                'net_price': '22.00',
                'local_tax_charges': '5.23',
                'duty_per_unit': '15.13',
                'gross_price_per_unit_invoicing_currency': {'unit': '', 'value': ''},
            },
        }
    )


@freeze_time('2012-01-14 03:21:34')
def test_ui_progress_serializer():

    data = {'ui_progress': {'sectiona_a': {'is_complete': True, 'modified': datetime.now()}}}
    serializer = serializers.ExportPlanSerializer(data=data)
    serializer.is_valid()
    assert serializer.is_valid()
    assert serializer.data == {
        'ui_progress': {
            'sectiona_a': OrderedDict([('is_complete', True), ('date_last_visited', '2012-01-14T03:21:34+00:00')])
        }
    }


def test_payment_method_serializer():

    data = {
        'getting_paid': {
            'payment_method': {'methods': ['BACS', 'BT'], 'notes': 'method 1'},
            'payment_terms': {'terms': 'TMP', 'notes': 'method 2'},
            'incoterms': {'transport': 'RME', 'notes': 'method 3'},
        }
    }
    serializer = serializers.ExportPlanSerializer(data=data)
    assert serializer.is_valid(raise_exception=True)

    assert serializer.validated_data == OrderedDict(
        [
            (
                'getting_paid',
                OrderedDict(
                    [
                        ('payment_method', OrderedDict([('methods', ['BACS', 'BT']), ('notes', 'method 1')])),
                        ('payment_terms', OrderedDict([('terms', 'TMP'), ('notes', 'method 2')])),
                        ('incoterms', OrderedDict([('transport', 'RME'), ('notes', 'method 3')])),
                    ]
                ),
            )
        ]
    )


def test_travel_business_policies_serializer(export_plan_data):
    serializer = serializers.TravelBusinessPoliciesSerializer(data=export_plan_data['travel_business_policies'])
    serializer.is_valid()
    assert serializer.validated_data == OrderedDict(
        [
            ('travel_information', 'All travel to be business class'),
            ('cultural_information', 'Lots of culture'),
            (
                'visa_information',
                OrderedDict(
                    [
                        ('visa_required', True),
                        ('how_where_visa', 'uk'),
                        ('how_long', '10 Months'),
                        ('notes', 'no notes'),
                    ]
                ),
            ),
        ]
    )


def test_business_risks_serializer(export_plan_data):
    business_risks_data = export_plan_data['business_risks'][0]
    business_risks_data['companyexportplan'] = 1
    serializer = serializers.BusinessRisksSerializer(data=business_risks_data)
    serializer.is_valid()
    assert serializer.validated_data == OrderedDict(
        [
            ('risk', 'new risk'),
            ('contingency_plan', 'new contingency'),
            ('risk_likelihood', 'LIKELY'),
            ('risk_impact', 'MAJOR'),
            ('companyexportplan', 1),
            ('pk', 1),
        ]
    )
