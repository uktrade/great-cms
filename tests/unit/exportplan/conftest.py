from unittest import mock

import pytest

from exportplan.core import helpers as exportplan_helpers


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


@pytest.fixture(autouse=False)
def mock_upload_exportplan_pdf():
    patch = mock.patch('exportplan.core.helpers.upload_exportplan_pdf', return_value={})
    yield patch.start()
    patch.stop()
