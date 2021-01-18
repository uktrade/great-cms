from unittest import mock

import pytest

from exportplan import helpers as exportplan_helpers


@pytest.fixture(autouse=False)
def mock_get_population_data(population_data):
    patch = mock.patch.object(exportplan_helpers, 'get_population_data', return_value=population_data)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=False)
def mock_get_cia_world_factbook_data(cia_factbook_data):
    patch = mock.patch.object(exportplan_helpers, 'get_cia_world_factbook_data', return_value=cia_factbook_data)
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=False)
def mock_get_country_data(country_data):
    patch = mock.patch.object(exportplan_helpers, 'get_country_data', return_value=country_data)
    yield patch.start()
    patch.stop()


@pytest.fixture
def patch_get_export_plan(export_plan_data):
    # TODO merge this and above patch so we use singe unified way of getting export plan
    yield mock.patch('sso.models.get_exportplan', return_value=export_plan_data)


@pytest.fixture(autouse=False)
def mock_get_export_plan(patch_get_export_plan):
    yield patch_get_export_plan.start()
    try:
        patch_get_export_plan.stop()
    except RuntimeError:
        # may already be stopped explicitly in a test
        pass


@pytest.fixture(autouse=False)
def cost_and_pricing_serialized_result():
    return {
        "direct_costs": {"product_costs": "10.00", "labour_costs": "5.00", "other_direct_costs": "0.00"},
        "overhead_costs": {
            "product_adaption": "0.00",
            "freight_logistics": "0.00",
            "agent_distributor_fees": "0.00",
            "marketing": "1345.00",
            "insurance": "10.00",
            "other_overhead_costs": "0.00",
        },
        "total_cost_and_price": {
            "units_to_export_first_period": {"unit": "", "value": "0.00"},
            "units_to_export_second_period": {"unit": "", "value": "0.00"},
            "final_cost_per_unit": "0.00",
            "average_price_per_unit": "0.00",
            "net_price": "0.00",
            "local_tax_charges": "0.00",
            "duty_per_unit": "0.00",
            "gross_price_per_unit_invoicing_currency": {"unit": "", "value": "0.00"},
        },
    }
