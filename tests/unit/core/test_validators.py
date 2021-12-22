from unittest import mock

import pytest
from django.forms import ValidationError
from django.test import override_settings

from core.validators import is_valid_uk_postcode, validate_file_infection
from tests.helpers import create_response


@pytest.mark.parametrize(
    'postcode, raise_expected',
    (
        ('SW1A1AA', False),
        ('90201', True),
        ('postcode', True),
        ('', True),
        (' ', True),
        ('\t', True),
    ),
)
def test_is_valid_uk_postcode(postcode, raise_expected):

    try:
        is_valid_uk_postcode(postcode)
        if raise_expected:
            assert False, f'Excepted {postcode} to fail validation. It did not'
    except ValidationError:
        if not raise_expected:
            assert False, f'Excepted {postcode} to pass validation. It did not'


@override_settings(CLAM_AV_ENABLED=True)
@mock.patch('core.helpers.ClamAvClient.scan_chunked')
def test_validate_file_infection_positive_scan(mock_clam_av_client_scan):
    file = 'file'
    mock_response = create_response({'malware': True, 'reason': 'Win.Test.EICAR_HDB-1', 'time': 0.005419833003543317})
    mock_clam_av_client_scan.return_value = mock_response

    with pytest.raises(ValidationError) as exception:
        validate_file_infection(file)

    assert 'Rejected: uploaded file did not pass security scan' in str(exception.value)


@override_settings(CLAM_AV_ENABLED=True)
@mock.patch('core.helpers.ClamAvClient.scan_chunked')
def test_validate_file_infection_negative_scan(mock_clam_av_client_scan):
    file = 'file'
    mock_response = create_response({'malware': False, 'reason': None, 'time': 0.011951766995480284})
    mock_clam_av_client_scan.return_value = mock_response

    try:
        validate_file_infection(file)
    except ValidationError:
        pytest.fail('Should not raise a validator error.')
