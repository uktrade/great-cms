from unittest import mock

import pytest

from exportplan.core import data, helpers
from exportplan.core.processor import ExportPlanProcessor


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
    'ui_progress_data, complete, percentage_complete, ep_completed, next_section',
    [
        [
            {},
            0,
            0,
            False,
            {
                'title': 'About your business',
                'url': '/export-plan/1/about-your-business/',
                'image': 'about-the-business.png',
            },
        ],
        [
            {'about-your-business': {}},
            0,
            0,
            False,
            {
                'title': 'About your business',
                'url': '/export-plan/1/about-your-business/',
                'image': 'about-the-business.png',
            },
        ],
        [
            {'about-your-business': {'is_complete': False, 'date_last_visited': '2012-01-14T03:21:34+00:00'}},
            0,
            0,
            False,
            {
                'title': 'About your business',
                'url': '/export-plan/1/about-your-business/',
                'image': 'about-the-business.png',
            },
        ],
        [
            {'about-your-business': {'is_complete': True, 'date_last_visited': '2012-01-14T03:21:34+00:00'}},
            1,
            0.1,
            False,
            {
                'title': 'Business objectives',
                'url': '/export-plan/1/business-objectives/',
                'image': 'business-objectives.png',
            },
        ],
        [
            {
                'about-your-business': {'is_complete': True, 'date_last_visited': '2012-01-14T03:21:34+00:00'},
                'getting-paid': {'is_complete': True, 'date_last_visited': '2012-01-21T03:21:34+00:00'},
                'target-markets-research': {'is_complete': False, 'date_last_visited': '2012-01-25T03:21:34+00:00'},
                'business-risk': {'is_complete': False, 'date_last_visited': '2012-01-12T03:21:34+00:00'},
            },
            2,
            0.2,
            False,
            {
                'title': 'Target markets research',
                'url': '/export-plan/1/target-markets-research/',
                'image': 'target-market-research.png',
            },
        ],
    ],
)
@mock.patch.object(helpers, 'get_exportplan')
def test_export_plan_processor_calculate_ep_progress(
    mock_get_exportplan, export_plan_data, ui_progress_data, complete, percentage_complete, ep_completed, next_section
):
    export_plan_data.update({'ui_progress': ui_progress_data})
    mock_get_exportplan.return_value = export_plan_data
    ep_progress = ExportPlanProcessor(export_plan_data).calculate_ep_progress()
    assert ep_progress['sections_total'] == len(data.SECTION_SLUGS)
    assert ep_progress['sections_completed'] == complete
    assert ep_progress['percentage_completed'] == percentage_complete
    assert ep_progress['exportplan_completed'] is ep_completed
    assert ep_progress['next_section'] == next_section


@mock.patch.object(helpers, 'get_exportplan')
def test_export_plan_processor_calculate_ep_progress_complete(mock_get_exportplan, export_plan_data):
    export_plan_data.update(
        {
            'ui_progress': {
                s: {'is_complete': True, 'date_last_visited': '2012-01-14T03:21:34+00:00'} for s in data.SECTION_SLUGS
            }
        }
    )
    mock_get_exportplan.return_value = export_plan_data

    ep_progress = ExportPlanProcessor(export_plan_data).calculate_ep_progress()

    assert ep_progress['sections_total'] == len(data.SECTION_SLUGS)
    assert ep_progress['sections_completed'] == len(data.SECTION_SLUGS)
    assert ep_progress['percentage_completed'] == 1.0
    assert ep_progress['exportplan_completed'] is True
    assert ep_progress['next_section'] == {
        'title': 'About your business',
        'url': '/export-plan/1/about-your-business/',
        'image': 'about-the-business.png',
    }


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


@pytest.mark.parametrize(
    'export_plan_data, url ,expected',
    [
        [{'objectives': {'rationale': 'non'}, 'company_objectives': ['a']}, 'business-objectives/', 2],
        [{'objectives': {'rationale': ''}, 'company_objectives': ['a']}, 'business-objectives/', 1],
        [{'objectives': {}, 'company_objectives': ['a']}, 'business-objectives/', 1],
        [
            {'adaptation_target_market': {'labelling': 'non'}, 'target_market_documents': ['a']},
            'adapting-your-product/',
            2,
        ],
        [{'adaptation_target_market': {}, 'target_market_documents': ['a']}, 'adapting-your-product/', 1],
        [{'marketing_approach': {'resources': 'a'}, 'route_markets': ['a']}, 'marketing-approach/', 2],
        [{'marketing_approach': {}, 'route_markets': ['a']}, 'marketing-approach/', 1],
        [
            {'funding_and_credit': {'override_estimated_total_cost': 'a'}, 'funding_credit_options': ['a']},
            'funding-and-credit/',
            2,
        ],
        [{'funding_and_credit': {}, 'funding_credit_options': ['a']}, 'funding-and-credit/', 1],
        [{'travel_business_policies': {'visa_information': 'a'}, 'business_trips': ['a']}, 'travel-plan/', 2],
        [{'travel_business_policies': {}, 'business_trips': ['a']}, 'travel-plan/', 1],
        [{'business_trips': []}, 'business-risk/', 0],
        [{'business_trips': ['1']}, 'business-risk/', 1],
    ],
)
def test_export_plan_processor_calculate_ep_section_progress_lists(user, export_plan_data, url, expected):
    export_plan_data.update({'pk': 1})
    export_plan_parser = ExportPlanProcessor(export_plan_data)
    progress = {
        item['url'].replace('/export-plan/1/', ''): item for item in export_plan_parser.calculate_ep_section_progress()
    }
    assert progress[url]['populated'] == expected
