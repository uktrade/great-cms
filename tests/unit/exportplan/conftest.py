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
