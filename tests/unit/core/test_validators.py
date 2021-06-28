import pytest
from django.forms import ValidationError

from core.validators import is_valid_uk_postcode


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
