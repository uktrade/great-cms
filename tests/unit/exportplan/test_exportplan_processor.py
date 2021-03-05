from unittest import mock

import pytest

from exportplan.core import data, helpers
from exportplan.core.processor import ExportPlanProcessor


def test_calculate_ep_section_progress(export_plan_data):
    progress = ExportPlanProcessor(export_plan_data).calculate_ep_section_progress()

    assert progress == {
        'about_your_business': {'total': 5, 'populated': 1},
        'objectives': {'total': 1, 'populated': 1},
        'target_markets_research': {'total': 5, 'populated': 0},
        'adaptation_target_market': {'total': 10, 'populated': 0},
        'marketing_approach': {'total': 1, 'populated': 1},
        'total_cost_and_price': {'total': 8, 'populated': 5},
        'getting_paid': {'total': 3, 'populated': 3},
        'funding_and_credit': {'total': 2, 'populated': 2},
        'travel_business_policies': {'total': 3, 'populated': 3},
    }


@pytest.mark.parametrize(
    'ui_progress_data, expected',
    [
        [{}, False],
        [{'target-markets': {'is_complete': True}}, False],
        [{'about-your-business': {}}, False],
        [{'about-your-business': {'is_complete': False}}, False],
        [{'about-your-business': {'is_complete': True}, 'Target-markets': {'is_complete': True}}, True],
    ],
)
def test_export_prcoessor_get_current_url_progress(ui_progress_data, expected):
    export_plan_data = {'ui_progress': ui_progress_data}
    current_url = ExportPlanProcessor(export_plan_data).build_current_url('about-your-business')
    assert current_url.get('is_complete') is expected


def test_export_plan_processor_get_current_url_country_required_not_in_check():
    export_plan_data = {'export_countries': []}
    current_url = ExportPlanProcessor(export_plan_data).build_current_url('about-your-business')
    assert current_url.get('country_required') is None


@pytest.mark.parametrize(
    'export_plan_data, expected',
    [
        [{'export_commodity_codes': [{'commodity_code': '220850', 'commodity_name': 'Gin'}]}, None],
        [{'export_commodity_codes': []}, True],
        [{'export_commodity_codes': None}, True],
    ],
)
def test_export_plan_processor_get_current_url_product_required(export_plan_data, expected):
    current_url = ExportPlanProcessor(export_plan_data).build_current_url('target-markets-research')
    assert current_url.get('product_required') == expected


def test_export_plan_processor_get_current_url_product_required_not_in_check():
    export_plan_data = {'export_commodity_codes': []}
    current_url = ExportPlanProcessor(export_plan_data).build_current_url('about-your-business')
    assert current_url.get('product_required') is None


@pytest.mark.parametrize(
    'ui_progress_data, complete, percentage_complete',
    [
        [{}, 0, 0],
        [{'a': {}}, 0, 0],
        [{'a': {'is_complete': False}}, 0, 0],
        [{'a': {'is_complete': True}}, 1, 0.1],
        [{'b': {'is_complete': True}, 'c': {'is_complete': True}}, 2, 0.2],
    ],
)
@mock.patch.object(helpers, 'get_exportplan')
def test_export_plan_processor_calculate_ep_progress(
    mock_get_exportplan, ui_progress_data, complete, percentage_complete
):
    export_plan_data = {'ui_progress': ui_progress_data}
    mock_get_exportplan.return_value = export_plan_data
    ep_progress = ExportPlanProcessor(export_plan_data).calculate_ep_progress()['export_plan_progress']
    assert ep_progress['sections_total'] == len(data.SECTION_SLUGS)
    assert ep_progress['sections_completed'] == complete
    assert ep_progress['percentage_completed'] == percentage_complete


def test_export_plan_processor_build_export_plan_sections(export_plan_data):
    sections = ExportPlanProcessor(export_plan_data).build_export_plan_sections()
    assert sections[0]['is_complete'] is True
    assert sections[1]['is_complete'] is False


def test_export_plan_processor_calculated_cost_pricing(cost_pricing_data):
    pricing_data = ExportPlanProcessor(cost_pricing_data).calculated_cost_pricing()
    assert pricing_data == {
        'calculated_cost_pricing': {
            'total_direct_costs': '15.00',
            'total_overhead_costs': '1355.00',
            'profit_per_unit': '6.00',
            'potential_total_profit': '132.00',
            'gross_price_per_unit': '42.36',
            'total_export_costs': '1685.00',
            'estimated_costs_per_unit': '76.59',
        }
    }


@pytest.mark.parametrize(
    'export_plan_data, expected',
    [
        [{'export_countries': [{'country_name': 'Netherlands', 'country_iso2_code': 'NL'}]}, None],
        [{'export_countries': []}, True],
        [{'export_countries': None}, True],
    ],
)
def test_export_plan_processor_get_current_url_country_required(export_plan_data, expected):
    current_url = ExportPlanProcessor(export_plan_data).build_current_url('target-markets-research')
    assert current_url.get('country_required') == expected


def test_export_plan_processor_calculate_ep_section_progress(user, export_plan_data, export_plan_section_progress_data):
    export_plan_parser = ExportPlanProcessor(export_plan_data)

    assert export_plan_parser.calculate_ep_section_progress() == export_plan_section_progress_data
