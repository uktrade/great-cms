from unittest import mock
import pytest
from exportplan import helpers


@pytest.fixture(autouse=True)
def mock_get_population_data():
    patch = mock.patch.object(
        helpers, 'get_population_data', return_value={'population_data': {'target_population': 10000}}
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_get_cia_world_factbook_data():
    patch = mock.patch.object(
        helpers, 'get_cia_world_factbook_data', return_value={'cia_factbook_data': {'languages': ['English']}}
    )
    yield patch.start()
    patch.stop()


@pytest.fixture(autouse=True)
def mock_get_country_data():
    patch = mock.patch.object(
        helpers, 'get_country_data', return_value={'population_data': {'cpi': 100}}
    )
    yield patch.start()
    patch.stop()
