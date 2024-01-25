from io import StringIO
from unittest.mock import patch

import pytest
import tablib
from django.core.management import call_command


@pytest.mark.parametrize('mgm_cmd', [('eyb_import_trade_associations')])
@pytest.mark.django_db
def test_import_eyb_data(mgm_cmd):
    with patch('core.helpers.get_s3_file_stream') as mock_work_function:
        with patch('tablib.import_set') as mock_import_set:
            mock_import_set.return_value = tablib.Dataset(
                [
                    'TRADE_ASSOCIATION_0001',
                    'Manufacturing, Energy and Infrastructure 1',
                    'UK H2 Mobility 1',
                    'http://www.ukh2mobility.co.uk/',
                    'Energy',
                    'Some test description here',
                ],
                [
                    'TRADE_ASSOCIATION_0002',
                    'Manufacturing, Food and Infrastructure 2',
                    'UK H2 Mobility 2',
                    'http://www.ukh2mobility.co.uk/',
                    'Food and Drink',
                    'Some test description here',
                ],
                [
                    'TRADE_ASSOCIATION_0003',
                    'Manufacturing, Technology and Infrastructure 3',
                    'UK H2 Mobility 3',
                    'http://www.ukh2mobility.co.uk/',
                    'Technology',
                    'Some test description here',
                ],
                headers=[
                    'trade_assocation_id',
                    'sector_grouping',
                    'association_name',
                    'website_link',
                    'sector',
                    'brief_description',
                ],
            )
            mock_work_function.return_value = None
            call_command(mgm_cmd, stdout=StringIO())
            assert mock_work_function.called


@pytest.mark.parametrize('mgm_cmd', [('eyb_import_salary_data')])
@pytest.mark.django_db
def test_import_eyb_salary_data(mgm_cmd):
    with patch('core.helpers.get_s3_file_stream') as mock_work_function:
        with patch('tablib.import_set') as mock_import_set:
            mock_import_set.return_value = tablib.Dataset(
                [
                    '1',
                    'Wales',
                    'not_used_col',
                    'not_used_col',
                    'Food and Drink',
                    'Entry-level',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    'x',
                    'not_used_col',
                    '22000',
                ],
                [
                    '2',
                    'West Midlands',
                    'not_used_col',
                    'not_used_col',
                    'Finance and Professional Services',
                    'Entry-level',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    '25000',
                    'not_used_col',
                    '26000',
                ],
                [
                    '3',
                    'United Kingdom',
                    'not_used_col',
                    'not_used_col',
                    'Technology & Smart Cities',
                    'Entry-level',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    '30000',
                    'not_used_col',
                    '32000',
                ],
                [
                    '4',
                    'West Midlands',
                    'not_used_col',
                    'not_used_col',
                    'Consumer and Retail',
                    'Entry-level',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    '',
                    'not_used_col',
                    '26000',
                ],
                headers=[
                    'id',
                    'region',
                    'not_used_col',
                    'not_used_col',
                    'vertical',
                    'professional_level',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    'median_salary',
                    'not_used_col',
                    'mean_salary',
                ],
            )
            mock_work_function.return_value = None
            call_command(mgm_cmd, stdout=StringIO())
            assert mock_work_function.called


@pytest.mark.parametrize('mgm_cmd', [('eyb_import_rent_data')])
@pytest.mark.django_db
def test_import_eyb_rent_data(mgm_cmd):
    with patch('core.helpers.get_s3_file_stream') as mock_work_function:
        with patch('tablib.import_set') as mock_import_set:
            mock_import_set.return_value = tablib.Dataset(
                ['1', 'Wales', '', '', '', 'Small Warehouses', '1.3', '5000', '10000'],
                ['2', 'West Midlands', '', '', '', 'Small Warehouses', '1.2', '5000', '15000'],
                ['3', 'Scotland', '', '', '', 'Small Warehouses', '1.1', '5000', '20000'],
                headers=[
                    'id',
                    'region',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    'not_used_col',
                    'gbp_per_sq_feet',
                    'square_feet',
                    'gbp_per_month',
                ],
            )
            mock_work_function.return_value = None
            call_command(mgm_cmd, stdout=StringIO())
            assert mock_work_function.called
